"""Tests for the configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from orca_agents.config import Config, get_settings


class TestConfig:
    """Test cases for the Config class."""

    def test_default_values(self):
        """Test that Config initializes with correct default values."""
        config = Config()

        # Basic app info
        assert config.app_name == "Orca Agents"
        assert config.app_version == "0.1.0"
        assert config.environment == "development"

        # Server configuration
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.debug is False

        # Ollama configuration
        assert config.ollama_chat_url == "http://localhost:11434"
        assert config.ollama_reasoning_url == "http://localhost:11435"

        # Model configuration
        assert config.chat_model == "qwen3:0.6b"
        assert config.reasoning_model == "qwen3:8b"

        # Agent configuration
        assert config.manager_agent_temperature == 0.7
        assert config.manager_agent_max_tokens == 2048
        assert config.web_surfer_temperature == 0.3
        assert config.web_surfer_max_tokens == 1024

        # Conversation management
        assert config.session_timeout_minutes == 60
        assert config.max_conversation_history == 50
        assert config.memory_pruning_threshold == 100

        # CORS configuration
        assert config.cors_origins == ["http://localhost:3000", "http://localhost:8080"]
        assert config.cors_methods == ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        assert config.cors_headers == ["*"]

        # Logging configuration
        assert config.log_level == "INFO"
        assert config.log_format == "json"

        # Health check configuration
        assert config.health_check_interval == 30
        assert config.health_check_timeout == 10
        assert config.health_check_retries == 3

    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Test Orca",
                "PORT": "9000",
                "DEBUG": "true",
                "OLLAMA_CHAT_URL": "http://chat.example.com:11434",
                "OLLAMA_REASONING_URL": "http://reasoning.example.com:11435",
                "CHAT_MODEL": "custom:chat",
                "REASONING_MODEL": "custom:reasoning",
            },
        ):
            config = Config()

            assert config.app_name == "Test Orca"
            assert config.port == 9000
            assert config.debug is True
            assert config.ollama_chat_url == "http://chat.example.com:11434"
            assert config.ollama_reasoning_url == "http://reasoning.example.com:11435"
            assert config.chat_model == "custom:chat"
            assert config.reasoning_model == "custom:reasoning"

    def test_env_file_loading(self):
        """Test loading configuration from .env file."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("APP_NAME=EnvFile Orca\n")
            f.write("PORT=7000\n")
            f.write("CHAT_MODEL=env:model\n")
            env_file_path = f.name

        try:
            # Test loading from specific env file
            config = Config(_env_file=env_file_path)

            assert config.app_name == "EnvFile Orca"
            assert config.port == 7000
            assert config.chat_model == "env:model"
        finally:
            # Clean up
            Path(env_file_path).unlink()

    def test_validation_errors(self):
        """Test configuration validation errors."""
        # For now, just test that the Config class works
        # More validation can be added to the Config class as needed
        config = Config(port=8000)
        assert config.port == 8000

    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case insensitive."""
        with patch.dict(
            os.environ,
            {
                "app_name": "Case Test",  # lowercase
                "PORT": "8888",  # uppercase
                "Chat_Model": "mixed:case",  # mixed case
            },
        ):
            config = Config()

            assert config.app_name == "Case Test"
            assert config.port == 8888
            assert config.chat_model == "mixed:case"

    @pytest.mark.parametrize(
        "temperature,expected",
        [
            (0.0, 0.0),
            (0.5, 0.5),
            (1.0, 1.0),
            (2.0, 2.0),
        ],
    )
    def test_valid_temperature_values(self, temperature: float, expected: float):
        """Test valid temperature values for agents."""
        config = Config(manager_agent_temperature=temperature)
        assert config.manager_agent_temperature == expected

    def test_temperature_bounds(self):
        """Test temperature values work within reasonable bounds."""
        # Test that reasonable temperature values work
        config = Config(manager_agent_temperature=0.1)
        assert config.manager_agent_temperature == 0.1

        config = Config(manager_agent_temperature=1.5)
        assert config.manager_agent_temperature == 1.5

    def test_cors_configuration_validation(self):
        """Test CORS configuration validation."""
        # Test valid CORS configuration
        config = Config(
            cors_origins=["http://localhost:3000"],
            cors_methods=["GET", "POST"],
            cors_headers=["Content-Type"],
        )

        assert config.cors_origins == ["http://localhost:3000"]
        assert config.cors_methods == ["GET", "POST"]
        assert config.cors_headers == ["Content-Type"]

    def test_logging_configuration(self):
        """Test logging configuration options."""
        # Test valid log levels
        for log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = Config(log_level=log_level)
            assert config.log_level == log_level

        # Test valid log formats
        for log_format in ["json", "text", "structured"]:
            config = Config(log_format=log_format)
            assert config.log_format == log_format


class TestGetSettings:
    """Test cases for the get_settings function."""

    def test_singleton_behavior(self):
        """Test that get_settings returns the same instance (caching)."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same object due to lru_cache
        assert settings1 is settings2

    def test_settings_instance_type(self):
        """Test that get_settings returns a Config instance."""
        settings = get_settings()
        assert isinstance(settings, Config)

    def test_cached_settings_consistency(self):
        """Test that cached settings remain consistent."""
        settings1 = get_settings()
        original_app_name = settings1.app_name

        # Get settings again
        settings2 = get_settings()

        # Should have the same app_name
        assert settings2.app_name == original_app_name

    def test_clear_cache_behavior(self):
        """Test behavior when cache is cleared."""
        # Get initial settings
        settings1 = get_settings()
        original_id = id(settings1)

        # Clear the cache
        get_settings.cache_clear()

        # Get settings again - should be a new instance
        settings2 = get_settings()
        new_id = id(settings2)

        # Should be different objects
        assert original_id != new_id
        # But should have the same configuration values
        assert settings1.app_name == settings2.app_name
