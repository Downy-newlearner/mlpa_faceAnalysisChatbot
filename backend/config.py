"""
Configuration management for the backend server.
Uses environment variables with pydantic-settings for validation.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI API
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    
    # Database
    database_url: str = "sqlite:///./storage/database.db"
    
    # File Storage
    upload_dir: str = "./storage/uploads"
    max_upload_size_mb: int = 50
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
STORAGE_DIR = PROJECT_ROOT / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
DATABASE_PATH = STORAGE_DIR / "database.db"

# Ensure directories exist
STORAGE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
