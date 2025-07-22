"""Multi-Agent Orchestrator for managing conversation flow and agent delegation."""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from smolagents import ActionStep, CodeAgent

from ..config import Config
from .factory import OllamaAgentFactory


class MultiAgentOrchestrator:
    """Orchestrates multiple agents for complex task handling with conversation management."""

    def __init__(self, config: Config):
        """Initialize the orchestrator.

        Args:
            config: Application configuration.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.factory = OllamaAgentFactory(config)

        # Conversation management
        self._conversations: dict[str, dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()

        # Multi-agent system components
        self._manager_agent: CodeAgent | None = None
        self._managed_agents: dict[str, dict[str, Any]] = {}

        # Initialize the multi-agent system
        self._setup_multi_agent_system()

    def _setup_multi_agent_system(self) -> None:
        """Set up the full multi-agent system with manager and worker agents."""
        try:
            # Create managed worker agents
            self._setup_managed_agents()

            # Create manager agent with worker delegation capabilities
            self._setup_manager_agent()

            self.logger.info(
                f"Multi-agent system initialized - Manager with {len(self._managed_agents)} workers"
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize multi-agent system: {e}")
            # Fallback to simple chat agent
            self._manager_agent = self.factory.create_chat_agent()
            self.logger.warning("Falling back to simple chat agent")

    def _setup_managed_agents(self) -> None:
        """Set up managed worker agents for specialization."""
        try:
            # Create web surfer managed agent configuration
            web_config = self.factory.create_managed_web_agent_config()
            self._managed_agents["web_searcher"] = web_config

            self.logger.debug("Created web surfer managed agent configuration")

            # Future: Add more specialized agents here
            # - Code analysis agent
            # - Data processing agent
            # - File management agent

        except Exception as e:
            self.logger.error(f"Failed to create managed agents: {e}")
            # Continue without managed agents - manager will work with basic tools

    def _setup_manager_agent(self) -> None:
        """Set up the manager agent with worker delegation capabilities."""
        try:
            # Convert managed agents configurations to list for the manager
            managed_agents_list = list(self._managed_agents.values())

            # Create manager agent with managed workers
            self._manager_agent = self.factory.create_manager_agent(
                tools=[],  # Manager delegates to workers, no direct tools
                max_steps=15,
                managed_agents=managed_agents_list,
            )

            # Add memory management callback
            self._manager_agent.step_callbacks = [self._create_memory_callback()]

            self.logger.info(
                f"Manager agent initialized with {len(managed_agents_list)} managed workers"
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize manager agent: {e}")
            raise

    def _create_memory_callback(self):
        """Create a callback for managing agent memory and logging."""

        def memory_callback(step: ActionStep):
            # Log agent actions for debugging
            self.logger.debug(f"Agent step: {step.action}")

            # Memory pruning to prevent context overflow
            if hasattr(step, "agent") and hasattr(step.agent, "memory"):
                current_steps = len(step.agent.memory.steps)
                max_steps = self.config.max_conversation_history

                if current_steps > max_steps:
                    self.logger.debug(f"Pruning memory: {current_steps} -> {max_steps}")
                    # Keep first step (system prompt) and recent steps
                    pruned_steps = (
                        step.agent.memory.steps[0:1]
                        + step.agent.memory.steps[-(max_steps - 1) :]
                    )
                    step.agent.memory.steps = pruned_steps

        return memory_callback

    async def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Get or create conversation context.

        Args:
            conversation_id: Unique conversation identifier.

        Returns:
            Conversation context dictionary.
        """
        async with self._cache_lock:
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = {
                    "created_at": datetime.now(UTC),
                    "last_activity": datetime.now(UTC),
                    "message_count": 0,
                    "agent_instance": None,  # Will be created on first use
                }
                self.logger.info(f"Created new conversation: {conversation_id}")

            # Update last activity
            self._conversations[conversation_id]["last_activity"] = datetime.now(UTC)

            return self._conversations[conversation_id]

    async def process_message(
        self,
        conversation_id: str,
        message: str,
        use_manager: bool = True,
        reset_context: bool = False,
    ) -> str:
        """Process a message through the appropriate agent.

        Args:
            conversation_id: Unique conversation identifier.
            message: User message to process.
            use_manager: Whether to use the manager agent (vs simple chat agent).
            reset_context: Whether to reset conversation context.

        Returns:
            Agent response to the message.
        """
        try:
            conversation = await self.get_conversation(conversation_id)

            # Determine which agent to use
            if use_manager and self._manager_agent:
                agent = self._manager_agent
                agent_type = "manager"

                # For manager agent, always use the same instance (it manages state internally)
                # but reset context based on conversation state
                should_reset = conversation["message_count"] == 0 or reset_context

            else:
                # Use or create simple chat agent for this conversation
                if conversation["agent_instance"] is None or reset_context:
                    conversation["agent_instance"] = self.factory.create_chat_agent()
                agent = conversation["agent_instance"]
                agent_type = "chat"

                # Reset on first message or when explicitly requested
                should_reset = conversation["message_count"] == 0 or reset_context

            self.logger.info(
                f"Processing message in {conversation_id} with {agent_type} agent "
                f"(reset={should_reset})"
            )

            # Process message with appropriate reset behavior
            response = agent.run(message, reset=should_reset)

            # Update conversation stats
            conversation["message_count"] += 1

            self.logger.info(f"Generated response for {conversation_id}")
            return response

        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            return f"I encountered an error: {str(e)}"

    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation from memory.

        Args:
            conversation_id: Conversation to clear.

        Returns:
            True if conversation was cleared, False if not found.
        """
        async with self._cache_lock:
            if conversation_id in self._conversations:
                del self._conversations[conversation_id]
                self.logger.info(f"Cleared conversation: {conversation_id}")
                return True
            return False

    async def get_conversation_stats(
        self, conversation_id: str
    ) -> dict[str, Any] | None:
        """Get statistics for a conversation.

        Args:
            conversation_id: Conversation to get stats for.

        Returns:
            Dictionary with conversation statistics or None if not found.
        """
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            return {
                "conversation_id": conversation_id,
                "created_at": conversation["created_at"].isoformat(),
                "last_activity": conversation["last_activity"].isoformat(),
                "message_count": conversation["message_count"],
                "has_agent_instance": conversation["agent_instance"] is not None,
            }
        return None

    async def list_active_conversations(self) -> list[str]:
        """List all active conversation IDs.

        Returns:
            List of active conversation IDs.
        """
        async with self._cache_lock:
            return list(self._conversations.keys())

    async def cleanup_stale_conversations(self, max_age_hours: int = 24) -> int:
        """Clean up conversations older than specified age.

        Args:
            max_age_hours: Maximum age in hours before cleanup.

        Returns:
            Number of conversations cleaned up.
        """
        from datetime import timedelta

        cutoff_time = datetime.now(UTC) - timedelta(hours=max_age_hours)
        cleaned_count = 0

        async with self._cache_lock:
            stale_conversations = [
                conv_id
                for conv_id, conv_data in self._conversations.items()
                if conv_data["last_activity"] < cutoff_time
            ]

            for conv_id in stale_conversations:
                del self._conversations[conv_id]
                cleaned_count += 1

            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} stale conversations")

        return cleaned_count

    def get_available_workers(self) -> dict[str, str]:
        """Get information about available worker agents.

        Returns:
            Dictionary mapping worker names to their descriptions.
        """
        return {
            name: config["description"] for name, config in self._managed_agents.items()
        }

    def get_system_status(self) -> dict[str, Any]:
        """Get status information about the multi-agent system.

        Returns:
            Dictionary with system status information.
        """
        return {
            "manager_agent_available": self._manager_agent is not None,
            "managed_agents_count": len(self._managed_agents),
            "available_workers": list(self._managed_agents.keys()),
            "active_conversations": len(self._conversations),
            "system_mode": "multi-agent" if self._managed_agents else "simple",
        }
