"""OpenAI embeddings service with rate limiting."""

import logging
import time
from collections import deque
from datetime import datetime, timedelta
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings

from src.config import get_settings
from src.core.exceptions import EmbeddingError, RateLimitError

logger = logging.getLogger(__name__)


class OpenAIRateLimiter:
    """Rate limiter for OpenAI API (configurable limits)."""
    
    def __init__(self, requests_per_minute: int = 3000, requests_per_day: int = 1000000):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute (default: 3000)
            requests_per_day: Maximum requests per day (default: 1M)
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        
        # Track requests in the last minute
        self.minute_window: deque = deque()
        
        # Track daily count
        self.daily_count = 0
        self.daily_reset = datetime.now() + timedelta(days=1)
    
    def _cleanup_old_requests(self) -> None:
        """Remove requests older than 1 minute from the window."""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        while self.minute_window and self.minute_window[0] < one_minute_ago:
            self.minute_window.popleft()
    
    def _reset_daily_count_if_needed(self) -> None:
        """Reset daily count if a day has passed."""
        now = datetime.now()
        if now >= self.daily_reset:
            self.daily_count = 0
            self.daily_reset = now + timedelta(days=1)
            logger.info("Daily rate limit reset")
    
    def can_make_request(self) -> bool:
        """Check if we can make a request within rate limits.
        
        Returns:
            True if we can make a request, False otherwise
        """
        self._cleanup_old_requests()
        self._reset_daily_count_if_needed()
        
        # Check daily limit
        if self.daily_count >= self.requests_per_day:
            return False
        
        # Check per-minute limit
        if len(self.minute_window) >= self.requests_per_minute:
            return False
        
        return True
    
    def record_request(self) -> None:
        """Record that a request was made."""
        now = datetime.now()
        self.minute_window.append(now)
        self.daily_count += 1
    
    def get_wait_time(self) -> float:
        """Get seconds to wait before the next request is allowed.
        
        Returns:
            Seconds to wait (0 if can make request now)
        """
        self._cleanup_old_requests()
        self._reset_daily_count_if_needed()
        
        # If daily limit reached, wait until tomorrow
        if self.daily_count >= self.requests_per_day:
            wait_seconds = (self.daily_reset - datetime.now()).total_seconds()
            return max(0, wait_seconds)
        
        # If per-minute limit reached, wait for oldest request to expire
        if len(self.minute_window) >= self.requests_per_minute:
            oldest = self.minute_window[0]
            wait_seconds = 60 - (datetime.now() - oldest).total_seconds()
            return max(0, wait_seconds)
        
        return 0.0
    
    def get_status(self) -> dict:
        """Get current rate limiter status.
        
        Returns:
            Dictionary with current status
        """
        self._cleanup_old_requests()
        self._reset_daily_count_if_needed()
        
        return {
            "requests_this_minute": len(self.minute_window),
            "requests_today": self.daily_count,
            "minute_limit": self.requests_per_minute,
            "daily_limit": self.requests_per_day,
            "can_make_request": self.can_make_request(),
            "wait_time_seconds": self.get_wait_time(),
            "daily_reset": self.daily_reset.isoformat()
        }


class OpenAIEmbeddingService:
    """Service for generating embeddings using OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI embedding service."""
        self.settings = get_settings()
        self.rate_limiter = OpenAIRateLimiter(
            requests_per_minute=self.settings.openai_max_rpm,
            requests_per_day=self.settings.openai_max_rpd
        )
        
        # Initialize OpenAI embeddings
        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=self.settings.openai_api_key
            )
            logger.info("OpenAI embedding service initialized with text-embedding-3-small")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {e}")
            raise EmbeddingError(f"Failed to initialize OpenAI embeddings: {e}")
    
    def _wait_for_rate_limit(self) -> None:
        """Wait if rate limit is exceeded."""
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.get_wait_time()
            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached. Waiting {wait_time:.1f} seconds..."
                )
                time.sleep(wait_time)
    
    def get_embedding(
        self,
        text: str,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> List[float]:
        """Get embedding for a single text.
        
        Args:
            text: Text to embed
            max_retries: Maximum number of retries on failure
            retry_delay: Delay between retries in seconds
        
        Returns:
            Embedding vector as list of floats
        
        Raises:
            RateLimitError: If rate limit is exceeded
            EmbeddingError: If embedding generation fails
        """
        for attempt in range(max_retries):
            try:
                # Check rate limit
                self._wait_for_rate_limit()
                
                # Generate embedding
                embedding = self.embeddings.embed_query(text)
                
                # Record successful request
                self.rate_limiter.record_request()
                
                logger.debug(f"Generated embedding for text (length: {len(text)})")
                return embedding
            
            except Exception as e:
                logger.warning(
                    f"Embedding generation failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise EmbeddingError(
                        f"Failed to generate embedding after {max_retries} attempts: {e}"
                    )
        
        raise EmbeddingError("Failed to generate embedding")
    
    def get_embeddings(
        self,
        texts: List[str],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> List[List[float]]:
        """Get embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            max_retries: Maximum number of retries on failure
            retry_delay: Delay between retries in seconds
        
        Returns:
            List of embedding vectors
        
        Raises:
            RateLimitError: If rate limit is exceeded
            EmbeddingError: If embedding generation fails
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = self.get_embedding(text, max_retries, retry_delay)
                embeddings.append(embedding)
                
                logger.debug(f"Generated embedding {i + 1}/{len(texts)}")
            
            except Exception as e:
                logger.error(f"Failed to generate embedding for text {i + 1}: {e}")
                raise
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def get_rate_limit_status(self) -> dict:
        """Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        return self.rate_limiter.get_status()
    
    @property
    def dimensions(self) -> int:
        """Get embedding dimensions for text-embedding-3-small.
        
        Returns:
            Number of dimensions (1536 for text-embedding-3-small)
        """
        return 1536
    
    @property
    def model_name(self) -> str:
        """Get the model name.
        
        Returns:
            Model name
        """
        return "text-embedding-3-small"


# Singleton instance
_embedding_service: Optional[OpenAIEmbeddingService] = None


def get_embedding_service() -> OpenAIEmbeddingService:
    """Get or create the singleton embedding service instance.
    
    Returns:
        OpenAIEmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = OpenAIEmbeddingService()
    return _embedding_service