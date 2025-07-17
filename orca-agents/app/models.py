"""Pydantic models for the Orca Agents API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: str | None = Field(
        default=None, description="Optional conversation ID for context"
    )
    model: str = Field(default="qwen3", description="AI model to use for the response")
    stream: bool = Field(default=False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""

    message: str
    conversation_id: str
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: int = Field(
        ..., description="Time taken to process the request in milliseconds"
    )
