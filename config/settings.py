"""
Configuration settings for the Chat Summarization API.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat Summarization and Insights API"
    DEBUG: bool = False
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "chat_summarization"
    
    # LLM settings
    GROK_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings to avoid reloading from environment."""
    return Settings()


settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) 