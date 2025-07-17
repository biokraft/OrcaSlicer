"""Configuration settings for Orca Agents."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    app_name: str = "Orca Agents"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Ollama Configuration
    ollama_url: str = "http://localhost:11434"
    default_model: str = "qwen:0.5b"
    ollama_timeout: int = 60

    # CORS Configuration
    cors_origins: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
