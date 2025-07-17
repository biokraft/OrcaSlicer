"""Multi-Agent Orchestrator for managing conversation flow and agent delegation."""

import logging
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime

from smolagents import CodeAgent, ActionStep

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
        self._conversations: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()
        
        # Initialize manager agent
        self._manager_agent: Optional[CodeAgent] = None
        self._setup_manager()

    def _setup_manager(self) -> None:
        """Set up the manager agent with managed worker agents."""
        try:
            # For Phase 1, use a simple manager agent
            # Phase 3 will implement full multi-agent delegation
            self._manager_agent = self.factory.create_manager_agent()
            
            # Add memory management callback
            self._manager_agent.step_callbacks = [self._create_memory_callback()]
            
            self.logger.info("Manager agent initialized (Phase 1 - simple mode)")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize manager agent: {e}")
            # Fallback to simple chat agent
            self._manager_agent = self.factory.create_chat_agent()

    def _create_memory_callback(self):
        """Create a callback for managing agent memory and logging."""
        def memory_callback(step: ActionStep):
            # Log agent actions for debugging
            self.logger.debug(f"Agent step: {step.action}")
            
            # Memory pruning to prevent context overflow
            if hasattr(step, 'agent') and hasattr(step.agent, 'memory'):
                current_steps = len(step.agent.memory.steps)
                max_steps = self.config.max_conversation_history
                
                if current_steps > max_steps:
                    self.logger.debug(f"Pruning memory: {current_steps} -> {max_steps}")
                    # Keep first step (system prompt) and recent steps
                    pruned_steps = (
                        step.agent.memory.steps[0:1] + 
                        step.agent.memory.steps[-(max_steps-1):]
                    )
                    step.agent.memory.steps = pruned_steps

        return memory_callback

    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get or create conversation context.
        
        Args:
            conversation_id: Unique conversation identifier.
            
        Returns:
            Conversation context dictionary.
        """
        async with self._cache_lock:
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = {
                    "created_at": datetime.utcnow(),
                    "last_activity": datetime.utcnow(),
                    "message_count": 0,
                    "agent_instance": None,  # Will be created on first use
                }
                self.logger.info(f"Created new conversation: {conversation_id}")
            
            # Update last activity
            self._conversations[conversation_id]["last_activity"] = datetime.utcnow()
            
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
            else:
                # Use or create simple chat agent for this conversation
                if conversation["agent_instance"] is None or reset_context:
                    conversation["agent_instance"] = self.factory.create_chat_agent()
                agent = conversation["agent_instance"]
                agent_type = "chat"
            
            self.logger.info(
                f"Processing message in {conversation_id} with {agent_type} agent"
            )
            
            # Process message with appropriate reset behavior
            # Reset on first message or when explicitly requested
            should_reset = conversation["message_count"] == 0 or reset_context
            
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

    async def get_conversation_stats(self, conversation_id: str) -> Optional[Dict[str, Any]]:
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
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        async with self._cache_lock:
            stale_conversations = [
                conv_id for conv_id, conv_data in self._conversations.items()
                if conv_data["last_activity"] < cutoff_time
            ]
            
            for conv_id in stale_conversations:
                del self._conversations[conv_id]
                cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} stale conversations")
        
        return cleaned_count 