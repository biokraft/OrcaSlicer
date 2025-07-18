"""Tests for the Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from orca_agents.models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ModelsResponse,
)


class TestChatMessage:
    """Test cases for the ChatMessage model."""

    def test_valid_chat_message_creation(self):
        """Test creating a valid ChatMessage."""
        message = ChatMessage(role="user", content="Hello, how are you?")

        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert isinstance(message.timestamp, datetime)

    def test_chat_message_with_custom_timestamp(self):
        """Test ChatMessage with custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        message = ChatMessage(
            role="assistant",
            content="I'm doing well, thank you!",
            timestamp=custom_time,
        )

        assert message.timestamp == custom_time

    @pytest.mark.parametrize("role", ["user", "assistant", "system"])
    def test_valid_roles(self, role: str):
        """Test that valid roles are accepted."""
        message = ChatMessage(role=role, content="Test content")
        assert message.role == role

    def test_invalid_role(self):
        """Test that invalid roles raise ValidationError."""
        with pytest.raises(ValidationError):
            ChatMessage(role="invalid_role", content="Test content")

    def test_empty_content_allowed(self):
        """Test that empty content is allowed."""
        message = ChatMessage(role="user", content="")
        assert message.content == ""

    def test_message_serialization(self):
        """Test that ChatMessage can be serialized to dict."""
        message = ChatMessage(role="user", content="Test message")
        data = message.model_dump()

        assert "role" in data
        assert "content" in data
        assert "timestamp" in data
        assert data["role"] == "user"
        assert data["content"] == "Test message"


class TestChatRequest:
    """Test cases for the ChatRequest model."""

    def test_minimal_valid_request(self):
        """Test creating a minimal valid ChatRequest."""
        request = ChatRequest(message="Hello")

        assert request.message == "Hello"
        assert request.conversation_id is None
        assert request.model is None
        assert request.use_manager is False
        assert request.reset_context is False
        assert request.stream is False

    def test_full_chat_request(self):
        """Test creating a ChatRequest with all fields."""
        request = ChatRequest(
            message="Analyze this data",
            conversation_id="conv-123",
            model="qwen3:8b",
            use_manager=True,
            reset_context=True,
            stream=True,
        )

        assert request.message == "Analyze this data"
        assert request.conversation_id == "conv-123"
        assert request.model == "qwen3:8b"
        assert request.use_manager is True
        assert request.reset_context is True
        assert request.stream is True

    def test_message_length_validation(self):
        """Test message length validation."""
        # Test empty message (should fail)
        with pytest.raises(ValidationError):
            ChatRequest(message="")

        # Test very long message (should fail)
        long_message = "x" * 10001  # Exceeds max_length=10000
        with pytest.raises(ValidationError):
            ChatRequest(message=long_message)

        # Test valid length message
        valid_message = "x" * 5000  # Within limits
        request = ChatRequest(message=valid_message)
        assert len(request.message) == 5000

    def test_request_serialization(self):
        """Test that ChatRequest can be serialized."""
        request = ChatRequest(
            message="Test message", conversation_id="test-123", use_manager=True
        )

        data = request.model_dump()
        expected_keys = {
            "message",
            "conversation_id",
            "model",
            "use_manager",
            "reset_context",
            "stream",
        }
        assert set(data.keys()) == expected_keys

    def test_optional_fields_default_to_none_or_false(self):
        """Test that optional fields have correct defaults."""
        request = ChatRequest(message="Test")

        # Optional string fields should default to None
        assert request.conversation_id is None
        assert request.model is None

        # Boolean fields should default to False
        assert request.use_manager is False
        assert request.reset_context is False
        assert request.stream is False


class TestChatResponse:
    """Test cases for the ChatResponse model."""

    def test_valid_chat_response(self):
        """Test creating a valid ChatResponse."""
        response = ChatResponse(
            message="Hello! How can I help you?",
            conversation_id="conv-123",
            model="qwen3:0.6b",
            processing_time_ms=250,
        )

        assert response.message == "Hello! How can I help you?"
        assert response.conversation_id == "conv-123"
        assert response.model == "qwen3:0.6b"
        assert response.processing_time_ms == 250
        assert isinstance(response.timestamp, datetime)

    def test_response_with_custom_timestamp(self):
        """Test ChatResponse with custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        response = ChatResponse(
            message="Response",
            conversation_id="conv-123",
            model="qwen3:8b",
            processing_time_ms=500,
            timestamp=custom_time,
        )

        assert response.timestamp == custom_time

    def test_response_serialization(self):
        """Test that ChatResponse can be serialized."""
        response = ChatResponse(
            message="Test response",
            conversation_id="test-123",
            model="test-model",
            processing_time_ms=100,
        )

        data = response.model_dump()
        expected_keys = {
            "message",
            "conversation_id",
            "model",
            "timestamp",
            "processing_time_ms",
        }
        assert set(data.keys()) == expected_keys

    def test_processing_time_validation(self):
        """Test processing time validation."""
        # Valid processing time
        response = ChatResponse(
            message="Test",
            conversation_id="test",
            model="test",
            processing_time_ms=1000,
        )
        assert response.processing_time_ms == 1000

        # Zero processing time (should be valid)
        response = ChatResponse(
            message="Test", conversation_id="test", model="test", processing_time_ms=0
        )
        assert response.processing_time_ms == 0

    def test_empty_message_allowed(self):
        """Test that empty response message is allowed."""
        response = ChatResponse(
            message="", conversation_id="test", model="test", processing_time_ms=100
        )
        assert response.message == ""


class TestModelsResponse:
    """Test cases for the ModelsResponse model."""

    def test_valid_models_response(self):
        """Test creating a valid ModelsResponse."""
        response = ModelsResponse(
            models=["qwen3:0.6b", "qwen3:8b", "llama3:7b"],
            chat_model="qwen3:0.6b",
            reasoning_model="qwen3:8b",
        )

        assert response.models == ["qwen3:0.6b", "qwen3:8b", "llama3:7b"]
        assert response.chat_model == "qwen3:0.6b"
        assert response.reasoning_model == "qwen3:8b"

    def test_empty_models_list(self):
        """Test ModelsResponse with empty models list."""
        response = ModelsResponse(
            models=[], chat_model="default", reasoning_model="default"
        )

        assert response.models == []
        assert response.chat_model == "default"
        assert response.reasoning_model == "default"

    def test_single_model_in_list(self):
        """Test ModelsResponse with single model."""
        response = ModelsResponse(
            models=["qwen3:0.6b"], chat_model="qwen3:0.6b", reasoning_model="qwen3:0.6b"
        )

        assert len(response.models) == 1
        assert response.models[0] == "qwen3:0.6b"

    def test_models_response_serialization(self):
        """Test that ModelsResponse can be serialized."""
        response = ModelsResponse(
            models=["model1", "model2"], chat_model="model1", reasoning_model="model2"
        )

        data = response.model_dump()
        expected_keys = {"models", "chat_model", "reasoning_model"}
        assert set(data.keys()) == expected_keys
        assert isinstance(data["models"], list)

    def test_duplicate_models_allowed(self):
        """Test that duplicate models in list are allowed."""
        response = ModelsResponse(
            models=["qwen3:0.6b", "qwen3:0.6b", "qwen3:8b"],
            chat_model="qwen3:0.6b",
            reasoning_model="qwen3:8b",
        )

        assert len(response.models) == 3
        assert response.models.count("qwen3:0.6b") == 2


class TestModelValidation:
    """Test cross-model validation and edge cases."""

    def test_models_from_json(self):
        """Test creating models from JSON data."""
        # Test ChatRequest from JSON
        request_data = {
            "message": "Hello",
            "conversation_id": "test-123",
            "use_manager": True,
        }
        request = ChatRequest(**request_data)
        assert request.message == "Hello"
        assert request.use_manager is True

        # Test ChatResponse from JSON
        response_data = {
            "message": "Hi there!",
            "conversation_id": "test-123",
            "model": "qwen3:0.6b",
            "processing_time_ms": 150,
        }
        response = ChatResponse(**response_data)
        assert response.message == "Hi there!"
        assert response.processing_time_ms == 150

    def test_model_field_types(self):
        """Test that model fields have correct types."""
        request = ChatRequest(message="Test")

        # Check field types
        assert isinstance(request.message, str)
        assert isinstance(request.use_manager, bool)
        assert isinstance(request.reset_context, bool)
        assert isinstance(request.stream, bool)

    def test_field_type_validation(self):
        """Test field type validation and conversion."""
        # Test that invalid types for processing_time_ms raise ValidationError
        with pytest.raises(ValidationError):
            ChatResponse(
                message="Test",
                conversation_id="test",
                model="test",
                processing_time_ms="invalid",  # Should be int
            )

        # Test that valid types work correctly
        request = ChatRequest(message="Test message")
        assert isinstance(request.message, str)
        assert isinstance(request.use_manager, bool)
        assert isinstance(request.reset_context, bool)
        assert isinstance(request.stream, bool)
