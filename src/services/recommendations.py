"""Recommendation service for semantic book search."""

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from langchain_chroma import Chroma

from src.config import get_settings
from src.core.exceptions import VectorStoreError
from src.services.cache import get_query_cache
from src.services.embeddings import get_embedding_service

logger = logging.getLogger(__name__)


class Book:
    """Book recommendation result."""
    
    def __init__(self, row: pd.Series):
        """Initialize from pandas Series.
        
        Args:
            row: Pandas Series with book data
        """
        self.isbn13 = str(row["isbn13"])
        self.title = str(row["title"])
        self.authors = str(row["authors"])
        self.description = str(row["description"])
        self.category = str(row.get("simple_categories", "Unknown"))
        self.thumbnail = str(row.get("large_thumbnail", "assets/cover-not-found.jpg"))
        
        # Emotion scores
        self.joy = float(row.get("joy", 0))
        self.surprise = float(row.get("surprise", 0))
        self.anger = float(row.get("anger", 0))
        self.fear = float(row.get("fear", 0))
        self.sadness = float(row.get("sadness", 0))
        
    def format_authors(self) -> str:
        """Format author names nicely.
        
        Returns:
            Formatted author string
        """
        authors_split = self.authors.split(";")
        
        if len(authors_split) == 2:
            return f"{authors_split[0]} and {authors_split[1]}"
        elif len(authors_split) > 2:
            return f"{', '.join(authors_split[:-1])} and {authors_split[-1]}"
        else:
            return self.authors
    
    def truncate_description(self, max_words: int = 30) -> str:
        """Truncate description to specified word count.
        
        Args:
            max_words: Maximum number of words
        
        Returns:
            Truncated description
        """
        words = self.description.split()
        if len(words) <= max_words:
            return self.description
        return " ".join(words[:max_words]) + "..."
    
    def to_dict(self) -> dict:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "isbn13": self.isbn13,
            "title": self.title,
            "authors": self.authors,
            "description": self.description,
            "category": self.category,
            "thumbnail": self.thumbnail,
            "emotions": {
                "joy": self.joy,
                "surprise": self.surprise,
                "anger": self.anger,
                "fear": self.fear,
                "sadness": self.sadness
            }
        }


class RecommendationService:
    """Service for book recommendations using semantic search."""
    
    def __init__(self, books_csv_path: str = "data/books_with_emotions.csv"):
        """Initialize recommendation service.
        
        Args:
            books_csv_path: Path to books CSV file
        """
        self.settings = get_settings()
        self.cache = get_query_cache()
        self.embedding_service = get_embedding_service()
        
        # Load books data
        try:
            self.books = pd.read_csv(books_csv_path)
            self._prepare_books_data()
            logger.info(f"Loaded {len(self.books)} books from {books_csv_path}")
        except Exception as e:
            logger.error(f"Failed to load books data: {e}")
            raise VectorStoreError(f"Failed to load books data: {e}")
        
        # Initialize vector store
        try:
            self.vector_store = Chroma(
                persist_directory=str(self.settings.vector_store_path),
                embedding_function=self.embedding_service.embeddings
            )
            logger.info(f"Initialized vector store at {self.settings.vector_store_path}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise VectorStoreError(f"Failed to initialize vector store: {e}")
    
    def _prepare_books_data(self) -> None:
        """Prepare books data (thumbnails, etc.)."""
        # Add large thumbnails
        self.books["large_thumbnail"] = self.books["thumbnail"] + "&fife=w800"
        
        # Replace NaN thumbnails with placeholder
        self.books["large_thumbnail"] = np.where(
            self.books["large_thumbnail"].isna(),
            "assets/cover-not-found.jpg",
            self.books["large_thumbnail"]
        )
    
    def get_categories(self) -> List[str]:
        """Get list of available book categories.
        
        Returns:
            Sorted list of categories with "All" first
        """
        categories = ["All"] + sorted(self.books["simple_categories"].unique().tolist())
        return categories
    
    def get_tones(self) -> List[str]:
        """Get list of available emotional tones.
        
        Returns:
            List of tones with "All" first
        """
        return ["All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad"]
    
    def search(
        self,
        query: str,
        category: str = "All",
        tone: str = "All",
        initial_top_k: Optional[int] = None,
        final_top_k: Optional[int] = None
    ) -> List[Book]:
        """Search for book recommendations.
        
        Args:
            query: Search query
            category: Category filter ("All" for no filter)
            tone: Emotional tone filter ("All" for no filter)
            initial_top_k: Initial number of results from vector search
            final_top_k: Final number of results to return
        
        Returns:
            List of Book objects
        """
        initial_top_k = initial_top_k or self.settings.default_top_k
        final_top_k = final_top_k or self.settings.default_final_k
        
        # Generate cache key
        cache_key = f"search:{query}:{category}:{tone}:{initial_top_k}:{final_top_k}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for query: {query}")
            return cached_result
        
        # Perform search
        try:
            logger.info(f"Searching for: '{query}' (category={category}, tone={tone})")
            
            # Vector similarity search
            docs = self.vector_store.similarity_search(query=query, k=initial_top_k)
            
            # Extract ISBNs from results
            isbns = [int(doc.page_content.strip('"').split()[0]) for doc in docs]
            
            # Get book data for matching ISBNs
            books_df = self.books[self.books["isbn13"].isin(isbns)].head(initial_top_k)
            
            # Apply category filter
            if category != "All":
                books_df = books_df[books_df["simple_categories"] == category]
            
            # Apply tone sorting
            books_df = self._sort_by_tone(books_df, tone)
            
            # Take final top K
            books_df = books_df.head(final_top_k)
            
            # Convert to Book objects
            results = [Book(row) for _, row in books_df.iterrows()]
            
            # Cache the results
            self.cache.set(cache_key, results)
            
            logger.info(f"Found {len(results)} recommendations")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreError(f"Search failed: {e}")
    
    def _sort_by_tone(self, books_df: pd.DataFrame, tone: str) -> pd.DataFrame:
        """Sort books by emotional tone.
        
        Args:
            books_df: DataFrame of books
            tone: Emotional tone to sort by
        
        Returns:
            Sorted DataFrame
        """
        if tone == "All" or books_df.empty:
            return books_df
        
        # Make a copy to avoid SettingWithCopyWarning
        books_df = books_df.copy()
        
        # Map tone to emotion column
        emotion_mapping = {
            "Happy": "joy",
            "Surprising": "surprise",
            "Angry": "anger",
            "Suspenseful": "fear",
            "Sad": "sadness"
        }
        
        emotion_col = emotion_mapping.get(tone)
        if emotion_col and emotion_col in books_df.columns:
            books_df = books_df.sort_values(by=emotion_col, ascending=False)
            logger.debug(f"Sorted by {emotion_col} (tone: {tone})")
        
        return books_df
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear the recommendation cache."""
        self.cache.clear()
        logger.info("Recommendation cache cleared")


# Singleton instance
_recommendation_service: Optional[RecommendationService] = None


def get_recommendation_service(books_csv_path: str = "data/books_with_emotions.csv") -> RecommendationService:
    """Get or create the singleton recommendation service instance.
    
    Args:
        books_csv_path: Path to books CSV file
    
    Returns:
        RecommendationService instance
    """
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService(books_csv_path)
    return _recommendation_service