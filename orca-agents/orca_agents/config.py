"""Configuration management for Orca Agents backend."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration with validation for dual Ollama architecture."""

    # Basic app info
    app_name: str = Field(default="Orca Agents", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    debug: bool = Field(default=False, description="Debug mode")

    # Dual Ollama configuration
    ollama_chat_url: str = Field(
        default="http://localhost:11434",
        description="Chat Ollama server URL (fast, lightweight models)",
    )
    ollama_reasoning_url: str = Field(
        default="http://localhost:11435",
        description="Reasoning Ollama server URL (larger, more capable models)",
    )

    # Model configuration
    chat_model: str = Field(
        default="qwen3:0.6b",
        description="Chat model for quick responses (without ollama/ prefix)",
    )
    reasoning_model: str = Field(
        default="qwen3:8b",
        description="Reasoning model for complex tasks (without ollama/ prefix)",
    )

    # Agent configuration
    manager_agent_temperature: float = Field(
        default=0.7, description="Temperature for manager agent"
    )
    manager_agent_max_tokens: int = Field(
        default=2048, description="Max tokens for manager agent"
    )
    web_surfer_temperature: float = Field(
        default=0.3, description="Temperature for web surfer agent"
    )
    web_surfer_max_tokens: int = Field(
        default=1024, description="Max tokens for web surfer agent"
    )

    # Conversation management
    session_timeout_minutes: int = Field(
        default=60, description="Session timeout in minutes"
    )
    max_conversation_history: int = Field(
        default=50, description="Maximum conversation history to keep"
    )
    memory_pruning_threshold: int = Field(
        default=100, description="Memory pruning threshold"
    )

    # CORS configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )
    cors_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods",
    )
    cors_headers: list[str] = Field(default=["*"], description="Allowed CORS headers")

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Logging format")

    # Health check configuration
    health_check_interval: int = Field(
        default=30, description="Health check interval in seconds"
    )
    health_check_timeout: int = Field(
        default=10, description="Health check timeout in seconds"
    )
    health_check_retries: int = Field(default=3, description="Health check retries")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Config:
    """Get cached settings instance."""
    return Config()
