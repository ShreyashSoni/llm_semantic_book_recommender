"""Tests for the OpenAI embeddings service."""

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.core.exceptions import EmbeddingError, RateLimitError
from src.services.embeddings import OpenAIRateLimiter, OpenAIEmbeddingService


class TestOpenAIRateLimiter:
    """Tests for the OpenAIRateLimiter class."""
    
    def test_initialization(self):
        """Test rate limiter initialization."""
        limiter = OpenAIRateLimiter(requests_per_minute=10, requests_per_day=100)
        assert limiter.requests_per_minute == 10
        assert limiter.requests_per_day == 100
        assert len(limiter.minute_window) == 0
        assert limiter.daily_count == 0
    
    def test_can_make_request_initially(self):
        """Test that requests are allowed initially."""
        limiter = OpenAIRateLimiter()
        assert limiter.can_make_request() is True
    
    def test_record_request(self):
        """Test recording requests."""
        limiter = OpenAIRateLimiter()
        assert limiter.daily_count == 0
        assert len(limiter.minute_window) == 0
        
        limiter.record_request()
        assert limiter.daily_count == 1
        assert len(limiter.minute_window) == 1
    
    def test_per_minute_limit(self):
        """Test per-minute rate limiting."""
        limiter = OpenAIRateLimiter(requests_per_minute=3, requests_per_day=100)
        
        # Make 3 requests
        for i in range(3):
            assert limiter.can_make_request() is True
            limiter.record_request()
        
        # 4th request should be blocked
        assert limiter.can_make_request() is False
        assert limiter.get_wait_time() > 0
    
    def test_per_day_limit(self):
        """Test per-day rate limiting."""
        limiter = OpenAIRateLimiter(requests_per_minute=100, requests_per_day=5)
        
        # Make 5 requests
        for i in range(5):
            assert limiter.can_make_request() is True
            limiter.record_request()
        
        # 6th request should be blocked
        assert limiter.can_make_request() is False
    
    def test_cleanup_old_requests(self):
        """Test cleanup of old requests from minute window."""
        limiter = OpenAIRateLimiter(requests_per_minute=2, requests_per_day=100)
        
        # Add an old request
        old_time = datetime.now() - timedelta(minutes=2)
        limiter.minute_window.append(old_time)
        limiter.daily_count = 1
        
        # Cleanup should remove old request from minute window
        limiter._cleanup_old_requests()
        assert len(limiter.minute_window) == 0
        
        # But daily count should remain
        assert limiter.daily_count == 1
    
    def test_daily_reset(self):
        """Test daily count reset."""
        limiter = OpenAIRateLimiter()
        limiter.daily_count = 50
        
        # Set reset time to past
        limiter.daily_reset = datetime.now() - timedelta(hours=1)
        
        # Should reset on next check
        limiter._reset_daily_count_if_needed()
        assert limiter.daily_count == 0
        assert limiter.daily_reset > datetime.now()
    
    def test_get_status(self):
        """Test getting rate limiter status."""
        limiter = OpenAIRateLimiter(requests_per_minute=3000, requests_per_day=1000000)
        
        # Make a few requests
        for i in range(3):
            limiter.record_request()
        
        status = limiter.get_status()
        assert status["requests_this_minute"] == 3
        assert status["requests_today"] == 3
        assert status["minute_limit"] == 3000
        assert status["daily_limit"] == 1000000
        assert status["can_make_request"] is True
        assert "daily_reset" in status


class TestOpenAIEmbeddingService:
    """Tests for the OpenAIEmbeddingService class."""
    
    @pytest.fixture
    def mock_embeddings(self):
        """Mock OpenAIEmbeddings."""
        with patch('src.services.embeddings.OpenAIEmbeddings') as mock:
            # Mock embed_query to return a simple embedding
            mock_instance = Mock()
            mock_instance.embed_query.return_value = [0.1] * 1536
            mock.return_value = mock_instance
            yield mock
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings."""
        with patch('src.services.embeddings.get_settings') as mock:
            settings = Mock()
            settings.openai_api_key = "test_key"
            settings.openai_max_rpm = 3000
            settings.openai_max_rpd = 1000000
            mock.return_value = settings
            yield mock
    
    def test_initialization(self, mock_embeddings, mock_settings):
        """Test service initialization."""
        service = OpenAIEmbeddingService()
        assert service.embeddings is not None
        assert service.rate_limiter is not None
        assert service.dimensions == 1536
        assert service.model_name == "text-embedding-3-small"
    
    def test_get_embedding_success(self, mock_embeddings, mock_settings):
        """Test successful embedding generation."""
        service = OpenAIEmbeddingService()
        
        embedding = service.get_embedding("test text")
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
    
    def test_get_embedding_with_retry(self, mock_embeddings, mock_settings):
        """Test embedding generation with retry on failure."""
        service = OpenAIEmbeddingService()
        
        # Mock to fail twice then succeed
        service.embeddings.embed_query.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            [0.1] * 1536
        ]
        
        embedding = service.get_embedding("test text", max_retries=3, retry_delay=0.1)
        assert len(embedding) == 1536
    
    def test_get_embedding_max_retries_exceeded(self, mock_embeddings, mock_settings):
        """Test embedding generation failure after max retries."""
        service = OpenAIEmbeddingService()
        
        # Mock to always fail
        service.embeddings.embed_query.side_effect = Exception("API Error")
        
        with pytest.raises(EmbeddingError):
            service.get_embedding("test text", max_retries=2, retry_delay=0.1)
    
    def test_get_embeddings_multiple(self, mock_embeddings, mock_settings):
        """Test generating embeddings for multiple texts."""
        service = OpenAIEmbeddingService()
        
        texts = ["text 1", "text 2", "text 3"]
        embeddings = service.get_embeddings(texts)
        
        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)
    
    def test_rate_limit_status(self, mock_embeddings, mock_settings):
        """Test getting rate limit status."""
        service = OpenAIEmbeddingService()
        
        status = service.get_rate_limit_status()
        assert "requests_this_minute" in status
        assert "requests_today" in status
        assert "can_make_request" in status
    
    def test_singleton_pattern(self, mock_embeddings, mock_settings):
        """Test that get_embedding_service returns singleton instance."""
        from src.services.embeddings import get_embedding_service, _embedding_service
        
        # Clear singleton
        import src.services.embeddings as embeddings_module
        embeddings_module._embedding_service = None
        
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        
        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])