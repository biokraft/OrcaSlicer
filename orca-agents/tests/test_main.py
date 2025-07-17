"""Tests for the main FastAPI application."""

from fastapi.testclient import TestClient

from app.main import app

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
    assert "ollama_connected" in data
    assert data["service"] == "orca-agents"


def test_models_endpoint():
    """Test the models endpoint."""
    response = client.get("/api/models")
    # This might fail if Ollama is not running, which is expected in tests
    # We just check the structure
    assert response.status_code in [200, 500]  # 500 if Ollama not available
    if response.status_code == 200:
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)


def test_chat_endpoint_structure():
    """Test the chat endpoint with basic request structure."""
    chat_request = {
        "message": "Hello, this is a test message",
        "model": "qwen:0.5b",
        "stream": False,
    }

    response = client.post("/api/chat", json=chat_request)
    # This might fail if Ollama is not running or model not available
    # We accept both success and expected failure codes
    assert response.status_code in [200, 400, 500]

    if response.status_code == 200:
        data = response.json()
        assert "message" in data
        assert "conversation_id" in data
        assert "model" in data
        assert "timestamp" in data
        assert "processing_time_ms" in data
