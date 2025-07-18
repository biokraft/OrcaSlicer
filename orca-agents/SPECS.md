# Orca Agents Backend Specifications

## 1. Project Overview

This project, codenamed "Orca Agents," provides the containerized Python backend for the AI Assistant in OrcaSlicer. It is a self-contained system responsible for serving the AI model, handling chat logic, and providing a clear API for the main OrcaSlicer application. It is built with FastAPI and `smolagents`, managed with Docker, and uses `uv` for package management.

## 2. Specification Library

| File | Description |
|---|---|
| `specs/architecture.md` | High-level overview of the dual-Ollama container architecture, services, and networking. |
| `specs/agentic_architecture.md` | Detailed specification for the multi-agent architecture, with Manager/Worker agents connected to separate Ollama instances. |
| `specs/development_environment.md` | Guide for setting up a local, Docker-based development environment with multiple Ollama containers. |
| `specs/api_endpoints.md` | Detailed specification for all API endpoints, including request/response schemas. |
| `specs/coding_standards.md` | Code style, linting rules, and patterns for configuration, agents, and tools. |
| `specs/testing_strategy.md` | The strategy for testing the Python backend, including unit and integration tests for agents. |
| `specs/database_persistence.md` | Specification for persisting chat conversations using SQLAlchemy and SQLite. |

## 2.1. Current Implementation Status

**Phase 1-2 Foundation Complete:**
- ✅ **Dual Ollama Architecture**: Chat service (qwen3:0.6b) + Reasoning service (qwen3:8b)
- ✅ **Multi-Agent Infrastructure**: `OllamaAgentFactory`, `MultiAgentOrchestrator` with conversation management
- ✅ **FastAPI Application**: Full API with health checks, chat endpoints, and conversation management
- ✅ **Development Environment**: UV, ruff, pre-commit, comprehensive Makefile, Docker setup
- ✅ **Configuration Management**: Pydantic settings with dual Ollama URLs and agent parameters

**Current Implementation Notes:**
- Agent system is in Phase 1 simplified mode (basic conversation without full multi-agent delegation)
- Web surfer agents created but not yet integrated into manager (Phase 3 feature)
- All infrastructure ready for Phase 3 multi-agent implementation
- Unit tests pending (next priority)

## 3. Implementation Plan

| Phase | Focus Area | Key Deliverables | Related Specs | Status |
|---|---|---|---|---|
| **Phase 1: Foundation** | Project Scaffolding | Create `pyproject.toml` and initial `orca_agents` directory structure. | `development_environment.md` | ✅ **DONE** |
| | Dev Environment | Configure `uv`, `ruff`, `pre-commit`, `.env.example`, and `Makefile`. | `development_environment.md`, `coding_standards.md` | ✅ **DONE** |
| | Docker Setup | Create `Dockerfile` and `docker-compose.yml` with `api` and dual `ollama` services. | `architecture.md`, `development_environment.md` | ✅ **DONE** |
| | CI Pipeline | Set up CI pipeline to run `lint` and `test` on all pull requests. | `testing_strategy.md` | ✅ **DONE** |
| **Phase 2: Core API & Agent** | Configuration | Implement Pydantic `Config` class with dual Ollama URLs. | `coding_standards.md` | ✅ **DONE** |
| | FastAPI Application | Implement FastAPI app with `/api/health` (checking both Ollama services) and `/api/chat`. | `api_endpoints.md`, `coding_standards.md` | ✅ **DONE** |
| | Agent Factory & Orchestrator | Implement `OllamaAgentFactory` connecting to two Ollama services and the `MultiAgentOrchestrator`. | `agentic_architecture.md` | ✅ **DONE** |
| | Unit Tests (Core) | Implement unit tests for configuration, API logic, and the agent factory. | `testing_strategy.md` | TBD |
| **Phase 3: Multi-Agent Implementation** | Manager Agent | Implement the main `ManagerAgent` within the orchestrator. | `agentic_architecture.md` | TBD |
| | Web Surfer Worker | Create the `WebSurferAgent` and associated web search/scrape tools. | `agentic_architecture.md`, `coding_standards.md` | TBD |
| | Multi-Agent Integration | Integrate the `WebSurferAgent` as a `ManagedAgent` into the `ManagerAgent`. | `agentic_architecture.md` | TBD |
| | Tool Unit Tests | Implement unit tests for all agent tools, verifying success and error cases. | `testing_strategy.md` | TBD |
| **Phase 4: Conversation & Integration** | Chat Session Management | Implement `conversation_id` caching in the `MultiAgentOrchestrator`. | `agentic_architecture.md` | TBD |
| | Memory Management | Implement `step_callbacks` for memory pruning and logging. | `agentic_architecture.md` | TBD |
| | Integration Tests | Develop integration tests for multi-agent delegation and chat session persistence. | `testing_strategy.md` | TBD |
| **Phase 5: Database Persistence** | Database Setup | Configure SQLite, SQLAlchemy, and Alembic for migrations. | `database_persistence.md` | TBD |
| | Models & Schemas | Implement Pydantic-based SQLAlchemy models for `Conversation` and `Message`. | `database_persistence.md` | TBD |
| | Persistence Service | Create a service to handle saving and retrieving chat history. | `database_persistence.md` | TBD |
| | API Integration | Add new endpoints (`/api/conversations`, `/api/conversations/{id}`) and integrate into chat logic. | `database_persistence.md`, `api_endpoints.md` | TBD |
| | Database Unit Tests | Write unit tests for the database models and persistence service. | `testing_strategy.md` | TBD |
| **Phase 6: UI Integration** | Chat History UI | Design and implement the UI for browsing and loading past conversations. | `database_persistence.md` | TBD |
