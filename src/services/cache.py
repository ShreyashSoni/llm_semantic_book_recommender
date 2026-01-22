"""In-memory caching service."""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from src.config import get_settings

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL (Time To Live)."""
    
    def __init__(self, ttl_seconds: Optional[int] = None):
        """Initialize cache.
        
        Args:
            ttl_seconds: Time to live in seconds (default from settings)
        """
        self.settings = get_settings()
        self.ttl = ttl_seconds if ttl_seconds is not None else self.settings.cache_ttl
        self.cache: dict[str, tuple[Any, datetime]] = {}
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache initialized with TTL: {self.ttl} seconds")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Cache key as hex string
        """
        # Create a string representation of the arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = "|".join(key_parts)
        
        # Hash it for consistent length and avoid special characters
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a cached item is expired.
        
        Args:
            timestamp: Timestamp when item was cached
        
        Returns:
            True if expired, False otherwise
        """
        return datetime.now() - timestamp > timedelta(seconds=self.ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            
            if not self._is_expired(timestamp):
                self._hits += 1
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                # Remove expired item
                del self.cache[key]
                logger.debug(f"Cache expired: {key}")
        
        self._misses += 1
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, datetime.now())
        logger.debug(f"Cache set: {key}")
    
    def get_or_compute(self, key: str, compute_fn, *args, **kwargs) -> Any:
        """Get value from cache or compute and cache it.
        
        Args:
            key: Cache key
            compute_fn: Function to compute value if not cached
            *args: Arguments for compute_fn
            **kwargs: Keyword arguments for compute_fn
        
        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = self.get(key)
        
        if value is not None:
            return value
        
        # Compute the value
        logger.debug(f"Computing value for key: {key}")
        value = compute_fn(*args, **kwargs)
        
        # Cache it
        self.set(key, value)
        
        return value
    
    def invalidate(self, key: str) -> bool:
        """Invalidate (remove) a cache entry.
        
        Args:
            key: Cache key to invalidate
        
        Returns:
            True if key was in cache, False otherwise
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache invalidated: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self.cache)
        self.cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache cleared: {count} entries removed")
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if self._is_expired(timestamp)
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "entries": len(self.cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
            "ttl_seconds": self.ttl
        }


# Singleton instance for query caching
_query_cache: Optional[SimpleCache] = None


def get_query_cache() -> SimpleCache:
    """Get or create the singleton query cache instance.
    
    Returns:
        SimpleCache instance for queries
    """
    global _query_cache
    if _query_cache is None:
        _query_cache = SimpleCache()
    return _query_cache


# Singleton instance for embedding caching
_embedding_cache: Optional[SimpleCache] = None


def get_embedding_cache() -> SimpleCache:
    """Get or create the singleton embedding cache instance.
    
    Returns:
        SimpleCache instance for embeddings
    """
    global _embedding_cache
    if _embedding_cache is None:
        # Use longer TTL for embeddings (they don't change)
        settings = get_settings()
        _embedding_cache = SimpleCache(ttl_seconds=settings.cache_ttl * 24)  # 24 hours
    return _embedding_cache