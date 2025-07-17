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
| **Phase 1: Foundation** | Project Scaffolding | Create `pyproject.toml` and initial `orca_agents` directory structure. | `development_environment.md` | ✅ **DONE** |
| | Dev Environment | Configure `uv`, `ruff`, `pre-commit`, and create `Makefile` for common tasks. | `development_environment.md`, `coding_standards.md` | ✅ **DONE** |
| | Docker Setup | Create `Dockerfile.api` and `docker-compose.yml` for `api` and `ollama` services. | `architecture.md` | ✅ **DONE** |
| | CI Pipeline | Set up CI pipeline to run `lint` and `test` on all pull requests. | `testing_strategy.md` | ✅ **DONE** |
| **Phase 2: Core API & Agent** | FastAPI Application | Implement FastAPI app with `/api/health`, `/api/chat`, and Pydantic models. | `api_endpoints.md`, `coding_standards.md` | TBD |
| | Manager Agent | Implement the main `ManagerAgent` with `LiteLLMModel` integration for Ollama. | `agentic_architecture.md` | TBD |
| | Unit Tests (Core) | Implement unit tests for API logic and core utilities, mocking external services. | `testing_strategy.md` | TBD |
| | Chat Session Management | Implement `conversation_id` logic to manage stateful conversations. | `api_endpoints.md`, `agentic_architecture.md` | TBD |
| **Phase 3: Worker Agents & Tools** | Web Surfer Agent | Create the `WebSurferAgent` worker with search and scrape tools. | `agentic_architecture.md` | TBD |
| | Tool Unit Tests | Implement unit tests for all agent tools, verifying success and error cases. | `testing_strategy.md` | TBD |
| | Multi-Agent Integration | Integrate the `WebSurferAgent` as a `ManagedAgent` into the `ManagerAgent`. | `agentic_architecture.md` | TBD |
| **Phase 4: Advanced Features & Testing** | Memory Pruning | Implement a `step_callbacks` function for robust conversation memory management. | `agentic_architecture.md` | TBD |
| | Integration Tests | Develop integration tests for multi-agent delegation and memory persistence. | `testing_strategy.md` | TBD |
| | Configuration | Finalize environment variable handling for all settings (e.g., model names, URLs). | `architecture.md` | TBD | 