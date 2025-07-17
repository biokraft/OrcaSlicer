# Architecture Specification

## 1. Purpose

This document provides a high-level overview of the backend system architecture. It defines the major components and their interactions, establishing the technical foundation for the Orca Agents project.

For detailed information on the agent-based implementation, please see the [Agentic Architecture Specification](agentic_architecture.md).
For production deployment details, see the [Production Deployment Specification](production_deployment.md).

## 2. System Components

The backend is designed as a multi-container Docker application, orchestrated with Docker Compose. This approach ensures separation of concerns and scalability.

- **`api` service**: The core FastAPI application serving the public-facing API. It contains the agentic logic built with `smolagents`.
- **`ollama-chat` service**: Runs an Ollama server dedicated to the primary, lightweight chat model (e.g., `qwen3:0.6b`). It will be exposed on port `11434`.
- **`ollama-reasoning` service**: Runs a separate Ollama server dedicated to the more powerful reasoning model (`qwen3:8b`). It will be exposed on a different port (e.g., `11435`).
- **`ollama-init` service**: A one-off service that runs on startup to pull the required LLM models for both the `ollama-chat` and `ollama-reasoning` services.

## 3. Network & Communication

- All services communicate over a private Docker bridge network (`app-network`).
- The `api` service communicates with the two Ollama services at their respective container names and ports:
    - `http://ollama-chat:11434`
    - `http://ollama-reasoning:11434` (Note: the internal port is the same, but the host port and service name differ).
- The FastAPI application is exposed to the host machine on a configurable port (e.g., `8000`).

## 4. Configuration

- Application configuration is managed via environment variables, loaded by a Pydantic `BaseSettings` class. This will now include separate base URLs for the chat and reasoning models.
- A `.env` file is used for local development, while production environments will have variables injected securely.

## 5. Logging and Monitoring

- All services are configured to use a `json-file` logging driver for structured logging.
- Both `ollama` services include health checks. The `api` service's health check must verify connectivity to both Ollama instances.
- For production, a dedicated monitoring stack (e.g., Prometheus) is specified in the [Production Deployment Specification](production_deployment.md). 