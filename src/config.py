"""
Configuration for Chloros Blog MCP Server.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
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
    log_level: str = "INFO"
    
    # Model Configuration
    openrouter_model: str = "anthropic/claude-3-haiku"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 512
    
    # Quality Configuration
    quality_pass_threshold: int = 80
    word_count_fail_threshold: float = -0.15
    max_retries: int = 3
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()