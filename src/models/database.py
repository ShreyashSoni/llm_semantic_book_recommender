"""Database models and session management."""

from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, Session, sessionmaker

from src.config import get_settings

Base = declarative_base()


class User(Base):
    """User model for tracking users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }


class SearchHistory(Base):
    """Search history model for tracking user searches."""
    
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    query = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tone = Column(String(100), nullable=True)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="search_history")
    
    def __repr__(self) -> str:
        return f"<SearchHistory(id={self.id}, query='{self.query[:50]}...')>"
    
    def to_dict(self) -> dict:
        """Convert search history to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query": self.query,
            "category": self.category,
            "tone": self.tone,
            "results_count": self.results_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Favorite(Base):
    """Favorite books model for tracking user favorites."""
    
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_isbn13 = Column(String(20), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    
    def __repr__(self) -> str:
        return f"<Favorite(id={self.id}, isbn={self.book_isbn13})>"
    
    def to_dict(self) -> dict:
        """Convert favorite to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_isbn13": self.book_isbn13,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Database engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            f"sqlite:///{settings.database_path}",
            connect_args={"check_same_thread": False}  # Needed for SQLite
        )
    return _engine


def get_session_factory():
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup.
    
    Usage:
        with get_db_session() as db:
            user = db.query(User).first()
    
    Yields:
        Database session
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution!)."""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)