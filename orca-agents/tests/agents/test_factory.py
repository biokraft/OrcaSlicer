"""Tests for the OllamaAgentFactory."""

from unittest.mock import Mock, patch

import pytest
from smolagents import LiteLLMModel, ToolCallingAgent

from orca_agents.agents.factory import OllamaAgentFactory
from orca_agents.config import Config


class TestOllamaAgentFactory:
    """Test cases for the OllamaAgentFactory class."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config(
            ollama_chat_url="http://test-chat:11434",
            ollama_reasoning_url="http://test-reasoning:11435",
            chat_model="test-chat:0.6b",
            reasoning_model="test-reasoning:8b",
        )

    @pytest.fixture
    def factory(self, config):
        """Create a factory instance for testing."""
        return OllamaAgentFactory(config)

    def test_factory_initialization(self, config):
        """Test that factory initializes correctly with config."""
        factory = OllamaAgentFactory(config)

        assert factory.config == config
        assert factory.logger is not None

    def test_create_model_with_chat_service(self, factory):
        """Test creating a model for the chat service."""
        model = factory.create_model("test-model", use_reasoning=False)

        assert isinstance(model, LiteLLMModel)
        assert model.model_id == "ollama/test-model"
        assert model.api_base == "http://test-chat:11434"

    def test_create_model_with_reasoning_service(self, factory):
        """Test creating a model for the reasoning service."""
        model = factory.create_model("test-model", use_reasoning=True)

        assert isinstance(model, LiteLLMModel)
        assert model.model_id == "ollama/test-model"
        assert model.api_base == "http://test-reasoning:11435"

    def test_create_model_adds_ollama_prefix(self, factory):
        """Test that create_model adds ollama/ prefix if not present."""
        # Model without prefix
        model = factory.create_model("plain-model")
        assert model.model_id == "ollama/plain-model"

        # Model with prefix (should not add another)
        model = factory.create_model("ollama/prefixed-model")
        assert model.model_id == "ollama/prefixed-model"

    @patch("orca_agents.agents.factory.CodeAgent")
    def test_create_manager_agent(self, mock_code_agent, factory):
        """Test creating a manager agent."""
        mock_agent_instance = Mock()
        mock_code_agent.return_value = mock_agent_instance

        agent = factory.create_manager_agent(tools=["test_tool"], max_steps=10)

        # Verify CodeAgent was called correctly
        mock_code_agent.assert_called_once()
        call_kwargs = mock_code_agent.call_args[1]

        assert call_kwargs["tools"] == ["test_tool"]
        assert isinstance(call_kwargs["model"], LiteLLMModel)
        assert call_kwargs["model"].model_id == "ollama/test-reasoning:8b"
        assert call_kwargs["model"].api_base == "http://test-reasoning:11435"

        assert agent == mock_agent_instance

    @patch("orca_agents.agents.factory.CodeAgent")
    def test_create_manager_agent_defaults(self, mock_code_agent, factory):
        """Test creating a manager agent with default parameters."""
        mock_agent_instance = Mock()
        mock_code_agent.return_value = mock_agent_instance

        factory.create_manager_agent()

        # Verify CodeAgent was called with empty tools by default
        mock_code_agent.assert_called_once()
        call_kwargs = mock_code_agent.call_args[1]

        assert call_kwargs["tools"] == []
        assert isinstance(call_kwargs["model"], LiteLLMModel)

    @patch("orca_agents.agents.factory.ToolCallingAgent")
    def test_create_web_surfer_agent_basic(self, mock_tool_agent, factory):
        """Test creating a web surfer agent."""
        mock_agent_instance = Mock()
        mock_tool_agent.return_value = mock_agent_instance

        agent = factory.create_web_surfer_agent(max_steps=5)

        # Verify ToolCallingAgent was called correctly
        mock_tool_agent.assert_called_once()
        call_kwargs = mock_tool_agent.call_args[1]

        # Tools list may be empty if import fails, which is handled gracefully
        assert "tools" in call_kwargs
        assert isinstance(call_kwargs["model"], LiteLLMModel)
        assert call_kwargs["model"].model_id == "ollama/test-chat:0.6b"
        assert agent == mock_agent_instance

    def test_create_web_surfer_agent_import_error_handling(self, factory):
        """Test that web surfer agent handles import errors gracefully."""
        # This should not raise an exception even if tools can't be imported
        agent = factory.create_web_surfer_agent()

        # Agent should be created successfully
        assert agent is not None
        assert isinstance(agent, ToolCallingAgent)

    def test_create_managed_web_agent(self, factory):
        """Test creating a managed web agent."""
        with patch.object(factory, "create_web_surfer_agent") as mock_create_web:
            mock_web_agent = Mock()
            mock_create_web.return_value = mock_web_agent

            agent = factory.create_managed_web_agent()

            mock_create_web.assert_called_once()
            assert agent == mock_web_agent

    @patch("orca_agents.agents.factory.CodeAgent")
    def test_create_chat_agent(self, mock_code_agent, factory):
        """Test creating a chat agent."""
        mock_agent_instance = Mock()
        mock_code_agent.return_value = mock_agent_instance

        factory.create_chat_agent(tools=["chat_tool"], max_steps=3)

        # Verify CodeAgent was called correctly
        mock_code_agent.assert_called_once()
        call_kwargs = mock_code_agent.call_args[1]

        assert call_kwargs["tools"] == ["chat_tool"]
        assert isinstance(call_kwargs["model"], LiteLLMModel)
        assert call_kwargs["model"].model_id == "ollama/test-chat:0.6b"
        assert call_kwargs["model"].api_base == "http://test-chat:11434"

    @patch("orca_agents.agents.factory.CodeAgent")
    def test_create_chat_agent_defaults(self, mock_code_agent, factory):
        """Test creating a chat agent with default parameters."""
        mock_agent_instance = Mock()
        mock_code_agent.return_value = mock_agent_instance

        factory.create_chat_agent()

        # Verify CodeAgent was called with empty tools by default
        mock_code_agent.assert_called_once()
        call_kwargs = mock_code_agent.call_args[1]

        assert call_kwargs["tools"] == []
        assert isinstance(call_kwargs["model"], LiteLLMModel)

    def test_model_service_selection_logic(self, factory):
        """Test that the correct service is selected based on use_reasoning parameter."""
        # Chat service
        chat_model = factory.create_model("test", use_reasoning=False)
        assert chat_model.api_base == "http://test-chat:11434"

        # Reasoning service
        reasoning_model = factory.create_model("test", use_reasoning=True)
        assert reasoning_model.api_base == "http://test-reasoning:11435"

    def test_logger_usage(self, factory):
        """Test that the factory uses logger for debugging."""
        with patch.object(factory.logger, "debug") as mock_debug:
            factory.create_model("test-model", use_reasoning=True)

            mock_debug.assert_called_once()
            call_args = mock_debug.call_args[0][0]
            assert "Creating model" in call_args
            assert "test-model" in call_args

    def test_factory_with_different_config(self):
        """Test factory behavior with different configuration values."""
        custom_config = Config(
            ollama_chat_url="http://custom-chat:9999",
            ollama_reasoning_url="http://custom-reasoning:8888",
            chat_model="custom-chat:1b",
            reasoning_model="custom-reasoning:13b",
        )

        factory = OllamaAgentFactory(custom_config)

        # Test chat model
        chat_model = factory.create_model(custom_config.chat_model, use_reasoning=False)
        assert chat_model.api_base == "http://custom-chat:9999"
        assert chat_model.model_id == "ollama/custom-chat:1b"

        # Test reasoning model
        reasoning_model = factory.create_model(
            custom_config.reasoning_model, use_reasoning=True
        )
        assert reasoning_model.api_base == "http://custom-reasoning:8888"
        assert reasoning_model.model_id == "ollama/custom-reasoning:13b"

    def test_logger_debug_usage(self, factory):
        """Test that the factory logs debug information."""
        with patch.object(factory.logger, "debug") as mock_debug:
            factory.create_model("test-model")

            # Should log debug information about model creation
            assert mock_debug.called

    @pytest.mark.parametrize(
        "model_input,expected_output",
        [
            ("simple-model", "ollama/simple-model"),
            ("ollama/already-prefixed", "ollama/already-prefixed"),
            ("model:tag", "ollama/model:tag"),
            ("ollama/model:tag", "ollama/model:tag"),
            ("namespace/model:tag", "ollama/namespace/model:tag"),
        ],
    )
    def test_model_prefix_handling(self, factory, model_input, expected_output):
        """Test various model naming scenarios for prefix handling."""
        model = factory.create_model(model_input)
        assert model.model_id == expected_output
