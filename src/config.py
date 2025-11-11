"""
Configuration management for the Chloros Blog MCP Server.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    # API Keys
    openai_api_key: str
    openrouter_api_key: str
    perplexity_api_key: str
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "medical"
    
    # Google Configuration
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str
    google_sheets_id: str
    google_published_folder_id: str
    
    # Server Configuration
    port: int = 3000
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    
    # Model Configuration
    openrouter_model: str = "anthropic/claude-3-haiku"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 512
    
    # Quality Configuration
    quality_pass_threshold: int = 80
    word_count_fail_threshold: float = -0.15
    max_retries: int = 3


# Global settings instance
settings = Settings()
