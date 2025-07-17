# Architecture Specification

## 1. Purpose

This document provides a high-level overview of the backend system architecture. It defines the major components and their interactions, establishing the technical foundation for the Orca Agents project.

For detailed information on the agent-based implementation, please see the [Agentic Architecture Specification](agentic_architecture.md).
For production deployment details, see the [Production Deployment Specification](production_deployment.md).

## 2. System Components

The backend is designed as a multi-container Docker application, orchestrated with Docker Compose. This approach ensures separation of concerns and scalability.

- **`api` service**: The core FastAPI application serving the public-facing API. It contains the agentic logic built with `smolagents`.
- **`ollama` service**: Runs the core Ollama server, providing LLM inference. It is configured with health checks to ensure reliability.
- **`ollama-init` service**: A one-off service that runs on startup to pull the required LLM models (`PRIMARY_MODEL`, `REASONING_MODEL`) from Ollama Hub. The `api` service will only start after this service completes successfully, ensuring models are available on first launch.

## 3. Network & Communication

- All services communicate over a private Docker bridge network (`app-network`).
- The `api` service communicates with the `ollama` service at `http://ollama:11434`.
- The FastAPI application is exposed to the host machine on a configurable port (e.g., `8000`).

## 4. Configuration

- Application configuration is managed via environment variables, loaded by a Pydantic `BaseSettings` class. This provides type-safe, validated configuration.
- A `.env` file is used for local development, while production environments will have variables injected securely.

## 5. Logging and Monitoring

- All services are configured to use a `json-file` logging driver for structured logging.
- The `ollama` service includes a health check to monitor its status, and the `api` service will implement its own `/api/health` endpoint.
- For production, a dedicated monitoring stack (e.g., Prometheus) is specified in the [Production Deployment Specification](production_deployment.md). 