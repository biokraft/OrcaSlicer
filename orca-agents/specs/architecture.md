# Architecture Specification

## 1. Purpose

This document provides a high-level overview of the backend system architecture. It defines the major components and their interactions, establishing the technical foundation for the Orca Agents project.

For detailed information on the agent-based implementation, please see the [Agentic Architecture Specification](agentic_architecture.md).

## 2. System Components

The backend consists of three primary services orchestrated with Docker Compose:

- **`api` service**: The core FastAPI application that serves the public-facing API. It houses the agent logic built with `smolagents`. It is defined in `Dockerfile.api`.
- **`ollama` service**: A container running the Ollama server, providing access to local LLMs like `qwen`. This service is pulled directly from the public Ollama image.
- **`dev-tools` service** (development only): A container with essential development and debugging tools.

## 3. Network & Communication

- The `api` service communicates with the `ollama` service over the internal Docker network. The base URL for the Ollama service will be managed via environment variables (e.g., `OLLAMA_BASE_URL=http://ollama:11434`).
- The FastAPI application will be exposed to the host machine on a designated port (e.g., `8000`).

## 4. Configuration

Application configuration (e.g., API keys, model names, Ollama URL) will be managed through environment variables and loaded at runtime, following 12-factor app principles. 