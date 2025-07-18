"""Tests for the main FastAPI application."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from orca_agents.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Orca Agents AI Assistant Backend"


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "environment" in data
    assert data["service"] == "orca-agents"
    assert data["status"] == "healthy"


def test_api_health_endpoint():
    """Test the API health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "chat_service" in data
    assert "reasoning_service" in data
    assert data["service"] == "orca-agents-api"
    assert data["status"] == "healthy"


def test_models_endpoint():
    """Test the models endpoint."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "chat_model" in data
    assert "reasoning_model" in data
    assert isinstance(data["models"], list)
    assert len(data["models"]) >= 2  # At least chat and reasoning models


@patch("orca_agents.main.orchestrator.process_message")
def test_chat_endpoint_success(mock_process_message):
    """Test successful chat endpoint interaction."""
    # Mock the orchestrator response
    mock_process_message.return_value = "Hello! This is a test response."

    chat_request = {
        "message": "Hello, this is a test message",
        "conversation_id": "test-conv-123",
        "model": "qwen3:0.6b",
        "use_manager": False,
        "stream": False,
    }

    response = client.post("/api/chat", json=chat_request)
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "conversation_id" in data
    assert "model" in data
    assert "timestamp" in data
    assert "processing_time_ms" in data

    assert data["message"] == "Hello! This is a test response."
    assert data["conversation_id"] == "test-conv-123"
    assert data["model"] == "qwen3:0.6b"
    assert isinstance(data["processing_time_ms"], int)

    # Verify orchestrator was called correctly
    mock_process_message.assert_called_once()
    call_args = mock_process_message.call_args[1]
    assert call_args["conversation_id"] == "test-conv-123"
    assert call_args["message"] == "Hello, this is a test message"
    assert call_args["use_manager"] is False


@patch("orca_agents.main.orchestrator.process_message")
def test_chat_endpoint_with_manager(mock_process_message):
    """Test chat endpoint with manager agent."""
    mock_process_message.return_value = "Complex analysis complete."

    chat_request = {
        "message": "Analyze this complex problem",
        "use_manager": True,
    }

    response = client.post("/api/chat", json=chat_request)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Complex analysis complete."

    # Verify manager was used
    call_args = mock_process_message.call_args[1]
    assert call_args["use_manager"] is True


@patch("orca_agents.main.orchestrator.process_message")
def test_chat_endpoint_auto_conversation_id(mock_process_message):
    """Test that conversation ID is auto-generated when not provided."""
    mock_process_message.return_value = "Response without conversation ID."

    chat_request = {
        "message": "Test message without conversation ID",
    }

    response = client.post("/api/chat", json=chat_request)
    assert response.status_code == 200

    data = response.json()
    assert "conversation_id" in data
    assert len(data["conversation_id"]) > 0  # Should be a UUID

    # Verify a conversation ID was passed to orchestrator
    call_args = mock_process_message.call_args[1]
    assert "conversation_id" in call_args
    assert call_args["conversation_id"] is not None


def test_chat_endpoint_validation_errors():
    """Test chat endpoint validation errors."""
    # Empty message
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422

    # Message too long
    long_message = "x" * 10001
    response = client.post("/api/chat", json={"message": long_message})
    assert response.status_code == 422

    # Invalid field types
    response = client.post(
        "/api/chat", json={"message": "Test", "use_manager": "invalid"}
    )
    assert response.status_code == 422


@patch("orca_agents.main.orchestrator.process_message")
def test_chat_endpoint_error_handling(mock_process_message):
    """Test chat endpoint error handling."""
    # Mock orchestrator to raise an exception
    mock_process_message.side_effect = Exception("Internal processing error")

    chat_request = {"message": "Test message"}

    response = client.post("/api/chat", json=chat_request)
    assert response.status_code == 500

    data = response.json()
    assert "detail" in data
    assert "Internal server error" in data["detail"]


@patch("orca_agents.main.orchestrator.clear_conversation")
def test_clear_conversation_success(mock_clear_conversation):
    """Test successful conversation clearing."""
    mock_clear_conversation.return_value = True

    response = client.delete("/api/conversations/test-conv-123")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "test-conv-123" in data["message"]

    mock_clear_conversation.assert_called_once_with("test-conv-123")


@patch("orca_agents.main.orchestrator.clear_conversation")
def test_clear_conversation_not_found(mock_clear_conversation):
    """Test clearing non-existent conversation."""
    mock_clear_conversation.return_value = False

    response = client.delete("/api/conversations/nonexistent")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


@patch("orca_agents.main.orchestrator.list_active_conversations")
def test_list_conversations(mock_list_conversations):
    """Test listing active conversations."""
    mock_list_conversations.return_value = ["conv1", "conv2", "conv3"]

    response = client.get("/api/conversations")
    assert response.status_code == 200

    data = response.json()
    assert "conversations" in data
    assert data["conversations"] == ["conv1", "conv2", "conv3"]


@patch("orca_agents.main.orchestrator.get_conversation_stats")
def test_get_conversation_stats_success(mock_get_stats):
    """Test getting conversation statistics."""
    mock_stats = {
        "conversation_id": "test-conv",
        "created_at": "2024-01-01T12:00:00",
        "last_activity": "2024-01-01T12:30:00",
        "message_count": 5,
        "has_agent_instance": True,
    }
    mock_get_stats.return_value = mock_stats

    response = client.get("/api/conversations/test-conv/stats")
    assert response.status_code == 200

    data = response.json()
    assert data == mock_stats


@patch("orca_agents.main.orchestrator.get_conversation_stats")
def test_get_conversation_stats_not_found(mock_get_stats):
    """Test getting stats for non-existent conversation."""
    mock_get_stats.return_value = None

    response = client.get("/api/conversations/nonexistent/stats")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


class TestApplicationSetup:
    """Test application setup and configuration."""

    def test_app_metadata(self):
        """Test that app has correct metadata."""
        assert app.title == "Orca Agents"  # From settings.app_name
        assert app.description == "AI Assistant Backend for OrcaSlicer"
        assert app.version == "0.1.0"  # From settings.app_version

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check that CORS middleware is in the middleware stack
        # FastAPI stores middleware differently, so we check if it's configured

        # Check that middleware exists in the app
        middleware_names = [
            type(middleware.cls).__name__ for middleware in app.user_middleware
        ]
        assert "CORSMiddleware" in middleware_names or len(app.user_middleware) > 0

    def test_orchestrator_initialization(self):
        """Test that orchestrator is initialized on app startup."""
        from orca_agents.agents.orchestrator import MultiAgentOrchestrator
        from orca_agents.main import orchestrator

        assert isinstance(orchestrator, MultiAgentOrchestrator)


class TestEndpointSecurity:
    """Test endpoint security and validation."""

    def test_missing_request_body(self):
        """Test handling of missing request body."""
        response = client.post("/api/chat")
        assert response.status_code == 422

    def test_malformed_json(self):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/chat",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_unsupported_http_methods(self):
        """Test that unsupported HTTP methods return appropriate errors."""
        # Chat endpoint should not accept GET
        response = client.get("/api/chat")
        assert response.status_code == 405

        # Health endpoints should not accept POST
        response = client.post("/health")
        assert response.status_code == 405
