"""User data service for managing search history and favorites."""

import logging
from datetime import datetime
from typing import List, Optional

from src.core.exceptions import DatabaseError
from src.models.database import (
    User,
    SearchHistory,
    Favorite,
    get_db_session
)

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user data."""
    
    def get_or_create_user(self, username: str = "default") -> int:
        """Get existing user or create new one.
        
        Args:
            username: Username to get or create
        
        Returns:
            User ID (integer)
        """
        try:
            with get_db_session() as db:
                user = db.query(User).filter_by(username=username).first()
                
                if user is None:
                    user = User(username=username)
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    logger.info(f"Created new user: {username}")
                else:
                    # Update last active
                    user.last_active = datetime.utcnow()
                    db.commit()
                    logger.debug(f"Retrieved existing user: {username}")
                
                # Return user_id to avoid detached instance issues
                return user.id
        except Exception as e:
            logger.error(f"Failed to get/create user: {e}")
            raise DatabaseError(f"Failed to get/create user: {e}")
    
    def save_search(
        self,
        user_id: int,
        query: str,
        category: str = "All",
        tone: str = "All",
        results_count: int = 0
    ) -> SearchHistory:
        """Save a search to history.
        
        Args:
            user_id: User ID
            query: Search query
            category: Category filter used
            tone: Tone filter used
            results_count: Number of results returned
        
        Returns:
            SearchHistory object
        """
        try:
            with get_db_session() as db:
                search = SearchHistory(
                    user_id=user_id,
                    query=query,
                    category=category if category != "All" else None,
                    tone=tone if tone != "All" else None,
                    results_count=results_count
                )
                db.add(search)
                db.commit()
                db.refresh(search)
                
                logger.debug(f"Saved search for user {user_id}: '{query}'")
                return search
        except Exception as e:
            logger.error(f"Failed to save search: {e}")
            raise DatabaseError(f"Failed to save search: {e}")
    
    def get_search_history(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        """Get user's search history.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of dictionaries with search history data
        """
        try:
            with get_db_session() as db:
                history = (
                    db.query(SearchHistory)
                    .filter_by(user_id=user_id)
                    .order_by(SearchHistory.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                    .all()
                )
                
                # Convert to dictionaries to avoid detached instance issues
                history_dicts = [
                    {
                        "id": search.id,
                        "query": search.query,
                        "category": search.category,
                        "tone": search.tone,
                        "results_count": search.results_count,
                        "created_at": search.created_at
                    }
                    for search in history
                ]
                
                logger.debug(f"Retrieved {len(history_dicts)} search history entries for user {user_id}")
                return history_dicts
        except Exception as e:
            logger.error(f"Failed to get search history: {e}")
            raise DatabaseError(f"Failed to get search history: {e}")
    
    def add_favorite(
        self,
        user_id: int,
        book_isbn13: str,
        notes: Optional[str] = None
    ) -> Favorite:
        """Add a book to user's favorites.
        
        Args:
            user_id: User ID
            book_isbn13: Book ISBN-13
            notes: Optional notes about the book
        
        Returns:
            Favorite object
        """
        try:
            with get_db_session() as db:
                # Check if already favorited
                existing = (
                    db.query(Favorite)
                    .filter_by(user_id=user_id, book_isbn13=book_isbn13)
                    .first()
                )
                
                if existing:
                    logger.debug(f"Book {book_isbn13} already in favorites for user {user_id}")
                    return existing
                
                favorite = Favorite(
                    user_id=user_id,
                    book_isbn13=book_isbn13,
                    notes=notes
                )
                db.add(favorite)
                db.commit()
                db.refresh(favorite)
                
                logger.info(f"Added favorite for user {user_id}: {book_isbn13}")
                return favorite
        except Exception as e:
            logger.error(f"Failed to add favorite: {e}")
            raise DatabaseError(f"Failed to add favorite: {e}")
    
    def remove_favorite(
        self,
        user_id: int,
        book_isbn13: str
    ) -> bool:
        """Remove a book from user's favorites.
        
        Args:
            user_id: User ID
            book_isbn13: Book ISBN-13
        
        Returns:
            True if removed, False if not found
        """
        try:
            with get_db_session() as db:
                favorite = (
                    db.query(Favorite)
                    .filter_by(user_id=user_id, book_isbn13=book_isbn13)
                    .first()
                )
                
                if favorite:
                    db.delete(favorite)
                    db.commit()
                    logger.info(f"Removed favorite for user {user_id}: {book_isbn13}")
                    return True
                
                logger.debug(f"Favorite not found for user {user_id}: {book_isbn13}")
                return False
        except Exception as e:
            logger.error(f"Failed to remove favorite: {e}")
            raise DatabaseError(f"Failed to remove favorite: {e}")
    
    def get_favorites(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Get user's favorite books.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of dictionaries with favorite data
        """
        try:
            with get_db_session() as db:
                favorites = (
                    db.query(Favorite)
                    .filter_by(user_id=user_id)
                    .order_by(Favorite.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                    .all()
                )
                
                # Convert to dictionaries to avoid detached instance issues
                favorite_dicts = [
                    {
                        "id": fav.id,
                        "book_isbn13": fav.book_isbn13,
                        "notes": fav.notes,
                        "created_at": fav.created_at
                    }
                    for fav in favorites
                ]
                
                logger.debug(f"Retrieved {len(favorite_dicts)} favorites for user {user_id}")
                return favorite_dicts
        except Exception as e:
            logger.error(f"Failed to get favorites: {e}")
            raise DatabaseError(f"Failed to get favorites: {e}")
    
    def is_favorite(
        self,
        user_id: int,
        book_isbn13: str
    ) -> bool:
        """Check if a book is in user's favorites.
        
        Args:
            user_id: User ID
            book_isbn13: Book ISBN-13
        
        Returns:
            True if favorited, False otherwise
        """
        try:
            with get_db_session() as db:
                exists = (
                    db.query(Favorite)
                    .filter_by(user_id=user_id, book_isbn13=book_isbn13)
                    .first()
                ) is not None
                
                return exists
        except Exception as e:
            logger.error(f"Failed to check favorite: {e}")
            raise DatabaseError(f"Failed to check favorite: {e}")
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with user stats
        """
        try:
            with get_db_session() as db:
                total_searches = (
                    db.query(SearchHistory)
                    .filter_by(user_id=user_id)
                    .count()
                )
                
                total_favorites = (
                    db.query(Favorite)
                    .filter_by(user_id=user_id)
                    .count()
                )
                
                user = db.query(User).get(user_id)
                
                return {
                    "user_id": user_id,
                    "username": user.username if user else "Unknown",
                    "total_searches": total_searches,
                    "total_favorites": total_favorites,
                    "member_since": user.created_at.isoformat() if user and user.created_at else None,
                    "last_active": user.last_active.isoformat() if user and user.last_active else None
                }
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            raise DatabaseError(f"Failed to get user stats: {e}")


# Singleton instance
_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """Get or create the singleton user service instance.
    
    Returns:
        UserService instance
    """
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service