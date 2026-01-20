"""
Application configuration management.

Uses pydantic-settings for type-safe configuration with validation.
"""
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
