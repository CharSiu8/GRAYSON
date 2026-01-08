# ================================================================================
# WHAT THIS FILE IS:
# Centralized configuration management for your application.
#
# WHY YOU NEED IT:
# - Keeps all settings in one place
# - Loads environment variables safely
# - Validates configuration at startup
# - Makes it easy to switch between dev/staging/production
#
# WHAT TO PUT IN IT:
# All configuration settings, loaded from environment variables or config files.
# ================================================================================

"""
Application configuration management.

Uses pydantic-settings for type-safe configuration with validation.
"""

# ---------------------------------------------------------
# OPTION 1: Using pydantic-settings (recommended)
# Type-safe, validates at startup, great developer experience
# ---------------------------------------------------------

# from pydantic_settings import BaseSettings
# from pydantic import Field
# from functools import lru_cache
#
#
# class Settings(BaseSettings):
#     """Application settings loaded from environment variables."""
#
#     # ----- Environment -----
#     environment: str = Field(default="development", description="Runtime environment")
#     debug: bool = Field(default=False, description="Debug mode")
#     log_level: str = Field(default="INFO", description="Logging level")
#
#     # ----- API Keys -----
#     openai_api_key: str = Field(..., description="OpenAI API key")
#     # anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
#
#     # ----- Vector Database -----
#     chroma_persist_directory: str = Field(default="./chroma_db", description="ChromaDB storage path")
#     # pinecone_api_key: str | None = Field(default=None)
#     # pinecone_environment: str | None = Field(default=None)
#
#     # ----- Server -----
#     host: str = Field(default="0.0.0.0", description="Server host")
#     port: int = Field(default=8000, description="Server port")
#
#     # ----- Model Settings -----
#     model_name: str = Field(default="gpt-4", description="LLM model to use")
#     embedding_model: str = Field(default="text-embedding-ada-002", description="Embedding model")
#     max_tokens: int = Field(default=4096, description="Maximum tokens per request")
#     temperature: float = Field(default=0.7, description="LLM temperature")
#
#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         case_sensitive = False
#
#
# @lru_cache
# def get_settings() -> Settings:
#     """
#     Get cached settings instance.
#     Using lru_cache ensures settings are only loaded once.
#     """
#     return Settings()


# ---------------------------------------------------------
# OPTION 2: Simple approach with python-dotenv
# Less type-safe but simpler for small projects
# ---------------------------------------------------------

# import os
# from dotenv import load_dotenv
#
# load_dotenv()
#
# # API Keys
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#
# # Settings
# ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# DEBUG = os.getenv("DEBUG", "false").lower() == "true"
#
# # Validate required settings
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY environment variable is required")


# ---------------------------------------------------------
# Placeholder - Remove when implementing
# ---------------------------------------------------------
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from dotenv import load_dotenv

# Explicitly load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    # API keys
    openai_api_key: str | None = Field(default=None)
    semantic_scholar_api_key: str | None = Field(default=None)
    discord_webhook_url: str | None = Field(default=None)

    # Vector DB / embeddings
    chroma_persist_directory: str = Field(default="./chroma_db")
    embedding_model: str = Field(default="text-embedding-3-small")
    chunk_size: int = Field(default=500)

    # LLM settings
    llm_mode: str = Field(default="api")  # "api" or "local"
    model_name: str = Field(default="gpt-3.5-turbo")

    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
