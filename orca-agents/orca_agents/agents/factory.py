"""Ollama Agent Factory for creating smolagents powered by dual Ollama instances."""

import logging
from typing import List, Optional

from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel

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
        system_prompt: Optional[str] = None,
        tools: Optional[List] = None,
        max_steps: int = 15,
    ) -> CodeAgent:
        """Create a manager agent using the reasoning model.
        
        Args:
            system_prompt: Custom system prompt for the agent (unused in current smolagents version).
            tools: List of tools available to the agent.
            max_steps: Maximum number of steps the agent can take.
            
        Returns:
            Configured CodeAgent for managing tasks and delegating to other agents.
        """
        model = self.create_model(self.config.reasoning_model, use_reasoning=True)

        # Note: CodeAgent in current smolagents version uses prompt_templates, not system_prompt
        return CodeAgent(
            tools=tools or [],
            model=model,
        )

    def create_web_surfer_agent(
        self,
        system_prompt: Optional[str] = None,
        max_steps: int = 8,
    ) -> ToolCallingAgent:
        """Create a web surfer agent for search and web browsing tasks.
        
        Args:
            system_prompt: Custom system prompt for the agent (unused in current smolagents version).
            max_steps: Maximum number of steps the agent can take.
            
        Returns:
            Configured ToolCallingAgent for web browsing tasks.
        """
        # Import tools here to avoid circular imports
        try:
            from smolagents.tools import DuckDuckGoSearchTool
            from smolagents.tools.web_search import VisitWebpageTool
            tools = [DuckDuckGoSearchTool(), VisitWebpageTool()]
        except ImportError:
            self.logger.warning("Web search tools not available, creating agent without tools")
            tools = []

        model = self.create_model(self.config.chat_model, use_reasoning=False)

        # Note: ToolCallingAgent in current smolagents version uses prompt_templates, not system_prompt
        return ToolCallingAgent(
            tools=tools,
            model=model,
        )

    def create_managed_web_agent(self) -> ToolCallingAgent:
        """Create a managed web surfer agent for delegation.
        
        Returns:
            ToolCallingAgent for web browsing tasks.
            
        Note:
            For Phase 1, we're using a simple ToolCallingAgent.
            In Phase 3, this will be enhanced with proper ManagedAgent wrapper.
        """
        return self.create_web_surfer_agent()

    def create_chat_agent(
        self,
        system_prompt: Optional[str] = None,
        tools: Optional[List] = None,
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
        ) 