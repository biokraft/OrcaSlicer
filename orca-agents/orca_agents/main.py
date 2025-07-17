"""Main FastAPI application for Orca Agents backend."""

import time
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agents import MultiAgentOrchestrator
from .config import get_settings
from .models import ChatRequest, ChatResponse, ModelsResponse

settings = get_settings()

# Initialize the multi-agent orchestrator
orchestrator = MultiAgentOrchestrator(settings)

app = FastAPI(
    title=settings.app_name,
    description="AI Assistant Backend for OrcaSlicer",
    version=settings.app_version,
)

# Configure CORS for the OrcaSlicer frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


@app.get("/health")
async def health_check() -> dict[str, str | bool]:
    """Health check endpoint."""
    # Simple health check - we can expand this to check Ollama services
    return {
        "status": "healthy",
        "service": "orca-agents",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/api/health")
async def api_health_check() -> dict[str, str | bool]:
    """Detailed API health check endpoint."""
    # TODO: Add actual Ollama health checks when we implement health monitoring
    return {
        "status": "healthy",
        "service": "orca-agents-api",
        "version": settings.app_version,
        "chat_service": "healthy",  # TODO: Check ollama-chat service
        "reasoning_service": "healthy",  # TODO: Check ollama-reasoning service
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Orca Agents AI Assistant Backend",
        "version": settings.app_version,
    }


@app.get("/api/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """List available AI models."""
    # Return the configured models for now
    return ModelsResponse(
        models=[settings.chat_model, settings.reasoning_model],
        chat_model=settings.chat_model,
        reasoning_model=settings.reasoning_model,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint for AI assistant interactions."""
    start_time = time.time()

    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Use the multi-agent orchestrator
        use_manager = request.model == settings.reasoning_model or request.use_manager

        response_message = await orchestrator.process_message(
            conversation_id=conversation_id,
            message=request.message,
            use_manager=use_manager,
            reset_context=getattr(request, "reset_context", False),
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            model=request.model
            or (settings.reasoning_model if use_manager else settings.chat_model),
            timestamp=datetime.now(),
            processing_time_ms=processing_time_ms,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e


@app.delete("/api/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str) -> dict[str, str]:
    """Clear a specific conversation."""
    cleared = await orchestrator.clear_conversation(conversation_id)
    if cleared:
        return {"message": f"Conversation {conversation_id} cleared successfully"}
    else:
        raise HTTPException(
            status_code=404, detail=f"Conversation {conversation_id} not found"
        )


@app.get("/api/conversations")
async def list_conversations() -> dict[str, list[str]]:
    """List all active conversations."""
    conversations = await orchestrator.list_active_conversations()
    return {"conversations": conversations}


@app.get("/api/conversations/{conversation_id}/stats")
async def get_conversation_stats(conversation_id: str) -> dict:
    """Get statistics for a specific conversation."""
    stats = await orchestrator.get_conversation_stats(conversation_id)
    if stats:
        return stats
    else:
        raise HTTPException(
            status_code=404, detail=f"Conversation {conversation_id} not found"
        )
