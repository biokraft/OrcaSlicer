# Backend Architecture Specification

## 1. Purpose

This document details the architecture of the Orca Agents backend, a containerized system designed for performance, scalability, and ease of development.

## 2. System Components

The backend consists of three core components orchestrated by Docker Compose:

1.  **API Server (`api` service):** A Python **FastAPI** application serving as the primary interface for the OrcaSlicer GUI.
2.  **Inference Server (`ollama` service):** A standard **Ollama** container that downloads, runs, and exposes LLMs.
3.  **Reverse Proxy (`caddy` service - Optional):** A Caddy container can be added for SSL termination, simplified routing, or to serve a potential web-based admin UI in the future.

## 3. Containerization

### 3.1. Dockerfile (`Dockerfile.api`)

-   **Base Image:** `python:3.13-slim` to keep the image size minimal.
-   **Package Installation:** Uses `uv` to install dependencies from `pyproject.toml` in a multi-stage build to optimize caching and reduce final image size.
-   **User:** Runs the application as a non-root user for enhanced security.
-   **Entrypoint:** Uses `uvicorn` to run the FastAPI application.

### 3.2. Docker Compose (`docker-compose.yml`)

-   **Services:** Defines the `api` and `ollama` services.
-   **Networking:** Both services share a custom bridge network (`orca-net`) to enable communication via service names (e.g., `http://ollama:11434`).
-   **Volumes:**
    -   A named volume (`ollama_data`) is used to persist downloaded LLM models, preventing re-downloads on container restarts.
    -   Bind mounts are used during development to hot-reload the FastAPI application on code changes.

## 4. Configuration Management

-   **Method:** Application configuration will be managed via environment variables.
-   **Loading:** Pydantic's `BaseSettings` will be used to load environment variables into a typed configuration object.
-   **Key Variables:**
    -   `OLLAMA_URL`: The URL for the Ollama service (e.g., `http://ollama:11434`).
    -   `LOG_LEVEL`: The application's logging level (e.g., `INFO`, `DEBUG`).
    -   `DEFAULT_MODEL`: The default Qwen3 model to use if none is specified by the client.

## 5. Asynchronous Processing

The entire stack is asynchronous to ensure high throughput and responsiveness.

-   **FastAPI:** Natively asynchronous.
-   **HTTPX:** The `httpx` library will be used to make non-blocking HTTP requests from the API server to the Ollama service.
-   **Streaming:** Responses from Ollama will be streamed back to the client, allowing the OrcaSlicer GUI to display the AI's response token-by-token. 