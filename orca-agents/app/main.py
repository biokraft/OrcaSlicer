"""Main FastAPI application for Orca Agents backend."""

import time
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models import ChatRequest, ChatResponse
from .services.ollama import ollama_service

settings = get_settings()

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
    ollama_healthy = await ollama_service.health_check()
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "service": "orca-agents",
        "ollama_connected": ollama_healthy,
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Orca Agents AI Assistant Backend",
        "version": settings.app_version,
    }


@app.get("/api/models")
async def list_models() -> dict[str, list[str]]:
    """List available AI models."""
    models = await ollama_service.list_models()
    return {"models": models}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint for AI assistant interactions."""
    start_time = time.time()

    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Generate response using Ollama
        response_message = await ollama_service.generate_response(
            message=request.message,
            model=request.model,
            stream=request.stream,
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            model=request.model,
            timestamp=datetime.now(),
            processing_time_ms=processing_time_ms,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing chat request: {str(e)}"
        ) from e
