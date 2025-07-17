# OrcaSlicer AI Assistant Backend

This directory contains the containerized AI backend system for OrcaSlicer's integrated chat assistant, powered by Qwen3 via Ollama.

## Architecture

```
┌─────────────────┐    HTTP     ┌─────────────────┐    HTTP     ┌─────────────────┐
│   OrcaSlicer    │──────────→  │   FastAPI       │──────────→  │     Ollama      │
│   (C++ GUI)     │             │   Server        │             │   (Qwen3 Model) │
│                 │←──────────   │                 │←──────────   │                 │
└─────────────────┘             └─────────────────┘             └─────────────────┘
```

## Components

- **FastAPI Server**: RESTful API interface for chat interactions
- **Ollama Container**: Hosts the Qwen3 model for local AI inference
- **Docker Compose**: Orchestrates both containers with networking
- **Makefile**: Simplifies build and deployment operations

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Make utility (usually pre-installed on Linux/macOS)

### Setup and Launch
```bash
# Build all containers
make build

# Start the AI system
make up

# Verify it's running
make status

# View logs
make logs

# Stop the system
make down
```

### API Endpoints

Once running, the FastAPI server will be available at `http://localhost:8000`

- `GET /health` - Health check endpoint
- `POST /chat` - Send chat messages to the AI
- `GET /models` - List available models
- `POST /models/switch` - Switch between different Qwen3 model sizes

### Example API Usage

```bash
# Health check
curl http://localhost:8000/health

# Send a chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does infill density affect in 3D printing?"}'
```

## Development

### Local Development
```bash
# Start in development mode with hot reload
make dev

# Run tests
make test

# View API documentation
# Navigate to http://localhost:8000/docs
```

### Configuration

Environment variables can be set in `.env` file:
```env
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
QWEN_MODEL=qwen3:8b
LOG_LEVEL=INFO
```

### Model Management

The system supports automatic model selection based on available hardware:
- Qwen3 0.6B - Minimal hardware requirements
- Qwen3 1.7B - Low-end systems
- Qwen3 8B - Mid-range systems (default)
- Qwen3 30B-A3B - High-end systems with 24GB+ VRAM

## Integration with OrcaSlicer

The C++ ChatPanel in OrcaSlicer communicates with this backend via HTTP requests:

```cpp
// Example C++ integration code
auto response = http_client.post("http://localhost:8000/chat", 
                                json_payload);
```

## Troubleshooting

### Common Issues

1. **Container won't start**: Check Docker daemon is running
2. **Model loading fails**: Ensure sufficient disk space for model downloads
3. **Connection refused**: Verify containers are up with `make status`

### Logs
```bash
# View all logs
make logs

# View specific service logs
docker-compose logs fastapi
docker-compose logs ollama
```

## License

This AI backend system is part of the OrcaSlicer project and follows the same licensing terms. 