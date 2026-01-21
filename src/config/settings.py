"""Application settings and configuration."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Semantic Book Recommender"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI API (Required)
    openai_api_key: str
    
    # Paths
    database_path: str = "./data/app.db"
    vector_store_path: str = "./vector_store"
    log_file: str = "./logs/app.log"
    
    # Cache settings
    cache_ttl: int = 3600  # 1 hour in seconds
    
    # Rate limiting (OpenAI)
    openai_max_rpm: int = 3000  # Requests per minute
    openai_max_rpd: int = 1000000  # Requests per day (1M)
    
    # Search settings
    default_top_k: int = 50  # Initial similarity search results
    default_final_k: int = 16  # Final results to display
    
    # Logging
    log_level: str = "INFO"
    
    # Gradio UI
    gradio_server_name: str = "0.0.0.0"
    gradio_server_port: int = 7860
    gradio_share: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def database_dir(self) -> Path:
        """Get database directory path."""
        return Path(self.database_path).parent
    
    @property
    def log_dir(self) -> Path:
        """Get log directory path."""
        return Path(self.log_file).parent
    
    @property
    def vector_store_dir(self) -> Path:
        """Get vector store directory path."""
        return Path(self.vector_store_path)
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.database_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.create_directories()
    return settings