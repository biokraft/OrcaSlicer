"""Ollama Agent Factory for creating smolagents powered by dual Ollama instances."""

import logging
from typing import Any

from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    ToolCallingAgent,
    VisitWebpageTool,
)

from ..config import Config


class OllamaAgentFactory:
    """Factory for creating smolagents powered by dual Ollama models."""

    def __init__(self, config: Config):
        """Initialize the factory with configuration.

        Args:
            config: Application configuration containing Ollama URLs and models.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def create_model(self, model_id: str, use_reasoning: bool = False) -> LiteLLMModel:
        """Create a LiteLLMModel instance for the appropriate Ollama service.

        Args:
            model_id: Model identifier (will be prefixed with 'ollama/' if needed).
            use_reasoning: If True, use the reasoning Ollama service, else chat service.

        Returns:
            Configured LiteLLMModel instance.
        """
        # Ensure proper ollama/ prefix
        if not model_id.startswith("ollama/"):
            model_id = f"ollama/{model_id}"

        # Select appropriate Ollama service
        api_base = (
            self.config.ollama_reasoning_url
            if use_reasoning
            else self.config.ollama_chat_url
        )

        self.logger.debug(f"Creating model {model_id} with base URL: {api_base}")

        return LiteLLMModel(
            model_id=model_id,
            api_base=api_base,
        )

    def create_manager_agent(
        self,
        system_prompt: str | None = None,
        tools: list | None = None,
        max_steps: int = 15,
        managed_agents: list[dict[str, Any]] | None = None,
    ) -> CodeAgent:
        """Create a manager agent using the reasoning model.

        Args:
            system_prompt: Custom system prompt for the agent (unused in current smolagents version).
            tools: List of tools available to the agent.
            max_steps: Maximum number of steps the agent can take.
            managed_agents: List of managed agent configurations for delegation.

        Returns:
            Configured CodeAgent for managing tasks and delegating to other agents.
        """
        model = self.create_model(self.config.reasoning_model, use_reasoning=True)

        # Create the manager agent
        manager = CodeAgent(
            tools=tools or [],
            model=model,
            max_steps=max_steps,
        )

        # Add managed agents for delegation if provided
        if managed_agents:
            manager.managed_agents = managed_agents
            self.logger.info(
                f"Manager agent configured with {len(managed_agents)} managed agents"
            )

        return manager

    def create_web_surfer_agent(
        self,
        system_prompt: str | None = None,
        max_steps: int = 8,
    ) -> ToolCallingAgent:
        """Create a web surfer agent for search and web browsing tasks.

        Args:
            system_prompt: Custom system prompt for the agent (unused in current smolagents version).
            max_steps: Maximum number of steps the agent can take.

        Returns:
            Configured ToolCallingAgent for web browsing tasks.
        """
        # Use built-in smolagents web tools
        try:
            tools = [DuckDuckGoSearchTool(), VisitWebpageTool()]
            self.logger.debug("Successfully loaded smolagents web browsing tools")
        except Exception as e:
            self.logger.warning(
                f"Web search tools not available: {e}, creating agent without tools"
            )
            tools = []

        model = self.create_model(self.config.chat_model, use_reasoning=False)

        # Note: ToolCallingAgent in current smolagents version uses prompt_templates, not system_prompt
        return ToolCallingAgent(
            tools=tools,
            model=model,
            max_steps=max_steps,
        )

    def create_managed_web_agent_config(self) -> dict[str, Any]:
        """Create a managed web surfer agent configuration for delegation.

        Returns:
            Dictionary configuration for a managed web agent that can be used with CodeAgent.

        Note:
            This creates the configuration that follows the smolagents multi-agent pattern.
        """
        # Create the specialized web surfer agent
        web_surfer = self.create_web_surfer_agent(max_steps=10)

        # Return configuration dict following smolagents pattern
        managed_config = {
            "agent": web_surfer,
            "name": "web_searcher",
            "description": (
                "An expert web surfer that can search the web for current information and "
                "visit webpages to extract content. Give it clear and specific queries to "
                "search for information, analyze web content, and provide comprehensive summaries. "
                "Best used for research tasks, fact-checking, and gathering current information."
            ),
        }

        self.logger.info(
            "Created managed web surfer agent configuration for delegation"
        )
        return managed_config

    def create_chat_agent(
        self,
        system_prompt: str | None = None,
        tools: list | None = None,
        max_steps: int = 5,
    ) -> CodeAgent:
        """Create a fast chat agent for simple conversational tasks.

        Args:
            system_prompt: Custom system prompt for the agent (unused in current smolagents version).
            tools: List of tools available to the agent.
            max_steps: Maximum number of steps the agent can take.

        Returns:
            Configured CodeAgent optimized for quick chat responses.
        """
        model = self.create_model(self.config.chat_model, use_reasoning=False)

        # Note: CodeAgent in current smolagents version uses prompt_templates, not system_prompt
        return CodeAgent(
            tools=tools or [],
            model=model,
            max_steps=max_steps,
        )
