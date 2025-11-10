"""
Configuration management for the Chloros Blog MCP Server.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # OpenRouter Configuration
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    
    # Perplexity Configuration
    perplexity_api_key: str = Field(..., env="PERPLEXITY_API_KEY")
    
    # Pinecone Configuration
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(..., env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="medical", env="PINECONE_INDEX_NAME")
    
    # Google Configuration
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    google_refresh_token: str = Field(..., env="GOOGLE_REFRESH_TOKEN")
    google_sheets_id: str = Field(..., env="GOOGLE_SHEETS_ID")
    google_published_folder_id: str = Field(..., env="GOOGLE_PUBLISHED_FOLDER_ID")
    
    # Server Configuration
    port: int = Field(default=3000, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Model Configuration
    openrouter_model: str = Field(default="anthropic/claude-3-haiku", env="OPENROUTER_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=512, env="EMBEDDING_DIMENSIONS")
    
    # Quality Configuration
    quality_pass_threshold: int = Field(default=80, env="QUALITY_PASS_THRESHOLD")
    word_count_fail_threshold: float = Field(default=-0.15, env="WORD_COUNT_FAIL_THRESHOLD")  # -15%
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
