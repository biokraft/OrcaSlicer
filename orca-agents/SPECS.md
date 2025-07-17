# Orca Agents Backend Specifications

## 1. Project Overview

This project, codenamed "Orca Agents," provides the containerized Python backend for the AI Assistant in OrcaSlicer. It is a self-contained system responsible for serving the AI model, handling chat logic, and providing a clear API for the main OrcaSlicer application. It is built with FastAPI and `smolagents`, managed with Docker, and uses `uv` for package management.

## 2. Specification Library

| File | Description |
|---|---|
| `specs/architecture.md` | High-level overview of the containerized backend architecture. |
| `specs/agentic_architecture.md` | Detailed specification for the `smolagents`-based multi-agent architecture. |
| `specs/development_environment.md` | Guide for setting up a local development environment using `uv` and Docker. |
| `specs/api_endpoints.md` | Detailed specification for all API endpoints, including request/response schemas. |
| `specs/coding_standards.md` | Code style, linting rules, and agent/tool development guidelines. |
| `specs/testing_strategy.md` | The strategy for testing the Python backend, including unit and integration tests for agents. |

## 3. Implementation Plan

| Phase | Focus Area | Key Deliverables | Related Specs | Status |
|---|---|---|---|---|
| **Phase 1: Foundation** | Project Scaffolding | Create `pyproject.toml` and initial directory structure for `orca_agents`. | `development_environment.md` | TBD |
| | Dev Environment | Configure `uv`, `ruff`, and `pre-commit` hooks. | `development_environment.md` | TBD |
| | Docker Setup | Create `Dockerfile.api` and `docker-compose.yml` for `api` and `ollama` services. | `architecture.md` | TBD |
| **Phase 2: Core API & Agent** | FastAPI Application | Basic FastAPI app with `/api/health` and `/api/chat` endpoints. | `api_endpoints.md` | TBD |
| | Manager Agent | Implement the main `ManagerAgent` with `LiteLLMModel` integration. | `agentic_architecture.md` | TBD |
| | Chat Session Management | Implement `conversation_id` logic to manage conversational state. | `api_endpoints.md` | TBD |
| **Phase 3: Worker Agents & Tools** | Web Surfer Agent | Create the `WebSurferAgent` worker with search and scrape tools. | `agentic_architecture.md` | TBD |
| | Tool Unit Tests | Implement unit tests for all tools, verifying success and error cases. | `testing_strategy.md` | TBD |
| | Multi-Agent Integration | Integrate the `WebSurferAgent` as a `ManagedAgent` into the `ManagerAgent`. | `agentic_architecture.md` | TBD |
| **Phase 4: Advanced Features & Testing** | Memory Pruning | Implement a `step_callbacks` function for robust memory management. | `agentic_architecture.md` | TBD |
| | Integration Tests | Develop integration tests for the multi-agent communication flow. | `testing_strategy.md` | TBD |
| | Configuration | Finalize environment variable handling for all configurable settings. | `architecture.md` | TBD | 