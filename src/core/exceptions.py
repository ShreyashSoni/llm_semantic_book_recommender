"""Custom exceptions for the book recommender."""


class BookRecommenderError(Exception):
    """Base exception for book recommender errors."""
    pass


class EmbeddingError(BookRecommenderError):
    """Error during embedding generation."""
    pass


class RateLimitError(EmbeddingError):
    """Rate limit exceeded for API calls."""
    pass


class VectorStoreError(BookRecommenderError):
    """Error with vector store operations."""
    pass


class DatabaseError(BookRecommenderError):
    """Error with database operations."""
    pass


class ConfigurationError(BookRecommenderError):
    """Error with application configuration."""
    pass