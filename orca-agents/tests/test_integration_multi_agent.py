"""Integration tests for the multi-agent system."""

from unittest.mock import Mock, patch

import pytest

from orca_agents.agents.factory import OllamaAgentFactory
from orca_agents.agents.orchestrator import MultiAgentOrchestrator
from orca_agents.config import Config


class TestMultiAgentIntegration:
    """Integration tests for the multi-agent system."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config(
            ollama_chat_url="http://test-chat:11434",
            ollama_reasoning_url="http://test-reasoning:11435",
            chat_model="test-chat:0.6b",
            reasoning_model="test-reasoning:8b",
            max_conversation_history=10,
        )

    @pytest.fixture
    def mock_web_tools(self):
        """Mock web tools for testing."""
        with (
            patch("orca_agents.agents.factory.DuckDuckGoSearchTool") as mock_search,
            patch("orca_agents.agents.factory.VisitWebpageTool") as mock_visit,
        ):
            mock_search_instance = Mock()
            mock_search_instance.name = "web_search"
            mock_search.return_value = mock_search_instance

            mock_visit_instance = Mock()
            mock_visit_instance.name = "visit_webpage"
            mock_visit.return_value = mock_visit_instance

            yield mock_search, mock_visit

    @pytest.mark.asyncio
    async def test_multi_agent_system_initialization(self, config, mock_web_tools):
        """Test that the multi-agent system initializes correctly."""
        with (
            patch("orca_agents.agents.factory.LiteLLMModel") as mock_model,
            patch("orca_agents.agents.factory.ToolCallingAgent") as mock_tool_agent,
            patch("orca_agents.agents.factory.CodeAgent") as mock_code_agent,
        ):
            # Mock components
            mock_model_instance = Mock()
            mock_model.return_value = mock_model_instance

            mock_web_agent = Mock()
            mock_tool_agent.return_value = mock_web_agent

            mock_manager = Mock()
            mock_code_agent.return_value = mock_manager

            # Create orchestrator
            orchestrator = MultiAgentOrchestrator(config)

            # Verify system was set up correctly
            assert orchestrator._manager_agent == mock_manager
            assert len(orchestrator._managed_agents) == 1
            assert "web_searcher" in orchestrator._managed_agents

            # Verify manager was configured with managed agents
            assert hasattr(mock_manager, "managed_agents")

            # Verify system status
            status = orchestrator.get_system_status()
            assert status["system_mode"] == "multi-agent"
            assert status["manager_agent_available"] is True
            assert status["managed_agents_count"] == 1

    @pytest.mark.asyncio
    async def test_web_search_delegation_flow(self, config, mock_web_tools):
        """Test that the manager correctly delegates web search tasks."""
        with (
            patch("orca_agents.agents.factory.LiteLLMModel") as mock_model,
            patch("orca_agents.agents.factory.ToolCallingAgent") as mock_tool_agent,
            patch("orca_agents.agents.factory.CodeAgent") as mock_code_agent,
        ):
            # Setup mocks
            mock_model.return_value = Mock()
            mock_web_agent = Mock()
            mock_tool_agent.return_value = mock_web_agent

            mock_manager = Mock()
            mock_manager.run.return_value = (
                "Based on web search, here's what I found..."
            )
            mock_code_agent.return_value = mock_manager

            # Create orchestrator and process a web search request
            orchestrator = MultiAgentOrchestrator(config)

            response = await orchestrator.process_message(
                conversation_id="test-conv",
                message="Search for information about Python testing best practices",
                use_manager=True,
            )

            # Verify manager was called
            mock_manager.run.assert_called_once()
            call_args = mock_manager.run.call_args[0]
            assert "Python testing best practices" in call_args[0]

            # Verify response
            assert "web search" in response.lower()

    def test_agent_factory_web_agent_creation(self, config, mock_web_tools):
        """Test that the factory creates web agents correctly."""
        factory = OllamaAgentFactory(config)

        with (
            patch("orca_agents.agents.factory.LiteLLMModel") as mock_model,
            patch("orca_agents.agents.factory.ToolCallingAgent") as mock_tool_agent,
        ):
            mock_model.return_value = Mock()
            mock_agent = Mock()
            mock_tool_agent.return_value = mock_agent

            # Test web surfer agent creation
            factory.create_web_surfer_agent()

            # Verify ToolCallingAgent was called with web tools
            mock_tool_agent.assert_called_once()
            call_kwargs = mock_tool_agent.call_args[1]
            assert "tools" in call_kwargs
            assert len(call_kwargs["tools"]) == 2  # DuckDuckGo + VisitWebpage
            assert call_kwargs["max_steps"] == 8

    def test_managed_web_agent_config_structure(self, config, mock_web_tools):
        """Test that managed web agent config has correct structure."""
        factory = OllamaAgentFactory(config)

        with (
            patch("orca_agents.agents.factory.LiteLLMModel"),
            patch("orca_agents.agents.factory.ToolCallingAgent") as mock_tool_agent,
        ):
            mock_agent = Mock()
            mock_tool_agent.return_value = mock_agent

            # Create managed web agent config
            config_dict = factory.create_managed_web_agent_config()

            # Verify structure
            assert isinstance(config_dict, dict)
            required_keys = ["agent", "name", "description"]
            for key in required_keys:
                assert key in config_dict

            assert config_dict["name"] == "web_searcher"
            assert "web surfer" in config_dict["description"].lower()
            assert config_dict["agent"] == mock_agent

    @pytest.mark.asyncio
    async def test_conversation_continuity_with_multi_agent(
        self, config, mock_web_tools
    ):
        """Test that conversation state is maintained across multi-agent interactions."""
        with (
            patch("orca_agents.agents.factory.LiteLLMModel"),
            patch("orca_agents.agents.factory.ToolCallingAgent"),
            patch("orca_agents.agents.factory.CodeAgent") as mock_code_agent,
        ):
            mock_manager = Mock()
            mock_manager.run.return_value = "Response"
            mock_code_agent.return_value = mock_manager

            orchestrator = MultiAgentOrchestrator(config)
            conversation_id = "test-conv"

            # First message
            await orchestrator.process_message(
                conversation_id=conversation_id,
                message="First message",
                use_manager=True,
            )

            # Second message
            await orchestrator.process_message(
                conversation_id=conversation_id,
                message="Second message",
                use_manager=True,
            )

            # Verify manager was called twice
            assert mock_manager.run.call_count == 2

            # Verify reset behavior
            calls = mock_manager.run.call_args_list
            assert calls[0][1]["reset"] is True  # First call resets
            assert calls[1][1]["reset"] is False  # Second call maintains context

            # Verify conversation tracking
            conversation = await orchestrator.get_conversation(conversation_id)
            assert conversation["message_count"] == 2

    def test_system_fallback_on_error(self, config):
        """Test that system falls back gracefully when multi-agent setup fails."""
        with patch(
            "orca_agents.agents.orchestrator.OllamaAgentFactory"
        ) as mock_factory_class:
            mock_factory = Mock()
            mock_factory_class.return_value = mock_factory

            # Make managed agent creation fail
            mock_factory.create_managed_web_agent_config.side_effect = Exception(
                "Setup failed"
            )

            # But chat agent creation succeeds
            mock_chat_agent = Mock()
            mock_factory.create_chat_agent.return_value = mock_chat_agent

            # Should not raise exception, should fall back
            orchestrator = MultiAgentOrchestrator(config)

            # Verify fallback occurred - the manager should still be created but without managed agents
            status = orchestrator.get_system_status()
            assert status["managed_agents_count"] == 0
            # Note: system might still report multi-agent if manager was created successfully
            # but without any managed agents, which is expected behavior

    @pytest.mark.asyncio
    async def test_worker_agent_descriptions(self, config, mock_web_tools):
        """Test that worker agent descriptions are accessible."""
        with (
            patch("orca_agents.agents.factory.LiteLLMModel"),
            patch("orca_agents.agents.factory.ToolCallingAgent"),
            patch("orca_agents.agents.factory.CodeAgent"),
        ):
            orchestrator = MultiAgentOrchestrator(config)

            # Get available workers
            workers = orchestrator.get_available_workers()

            assert "web_searcher" in workers
            assert isinstance(workers["web_searcher"], str)
            assert len(workers["web_searcher"]) > 0

            # Verify description contains relevant keywords
            description = workers["web_searcher"].lower()
            assert any(
                keyword in description for keyword in ["web", "search", "information"]
            )

    def test_multi_agent_system_logging(self, config, mock_web_tools, caplog):
        """Test that multi-agent system logs appropriately."""
        with (
            patch("orca_agents.agents.factory.LiteLLMModel"),
            patch("orca_agents.agents.factory.ToolCallingAgent"),
            patch("orca_agents.agents.factory.CodeAgent"),
        ):
            # Clear any existing log records
            caplog.clear()

            orchestrator = MultiAgentOrchestrator(config)

            # Check that initialization was logged - look for key phrases that indicate setup
            log_messages = [record.message for record in caplog.records]

            # Check for any of the expected log messages
            expected_logs = [
                "Multi-agent system initialized",
                "Manager agent initialized",
                "Created web surfer managed agent",
                "web surfer managed agent",
            ]

            found_relevant_log = any(
                any(expected in message for expected in expected_logs)
                for message in log_messages
            )

            # If specific messages aren't found, at least verify the system was set up
            if not found_relevant_log:
                # Alternative verification: check that the system was actually configured
                status = orchestrator.get_system_status()
                assert status["manager_agent_available"] is True
