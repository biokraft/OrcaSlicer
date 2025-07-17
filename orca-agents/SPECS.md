# Orca Agents Backend Specifications

## 1. Project Overview

This project, codenamed "Orca Agents," provides the containerized Python backend for the AI Assistant in OrcaSlicer. It is a self-contained system responsible for serving the AI model, handling chat logic, and providing a clear API for the main OrcaSlicer application. It is built with FastAPI and `smolagents`, managed with Docker, and uses `uv` for package management.

## 2. Specification Library

| File | Description |
|---|---|
| `specs/architecture.md` | High-level overview of the containerized backend architecture, including services and networking. |
| `specs/agentic_architecture.md` | Detailed specification for the `smolagents`-based multi-agent architecture, following the Manager-Worker pattern. |
| `specs/development_environment.md` | Guide for setting up a local, Docker-based development environment. |
| `specs/production_deployment.md`| Strategy for deploying the application to production, covering security, monitoring, and high availability. |
| `specs/api_endpoints.md` | Detailed specification for all API endpoints, including request/response schemas. |
| `specs/coding_standards.md` | Code style, linting rules, and patterns for configuration, agents, and tools. |
| `specs/testing_strategy.md` | The strategy for testing the Python backend, including unit and integration tests for agents. |

## 3. Implementation Plan

| Phase | Focus Area | Key Deliverables | Related Specs | Status |
|---|---|---|---|---|
| **Phase 1: Foundation** | Project Scaffolding | Create `pyproject.toml` and initial `orca_agents` directory structure. | `development_environment.md` | ✅ **DONE** |
| | Dev Environment | Configure `uv`, `ruff`, `pre-commit`, `.env.example`, and `Makefile`. | `development_environment.md`, `coding_standards.md` | TBD |
| | Docker Setup | Create `Dockerfile.api` and `docker-compose.yml` with `api`, `ollama`, and `ollama-init` services. | `architecture.md`, `development_environment.md` | TBD |
| | CI Pipeline | Set up CI pipeline to run `lint` and `test` on all pull requests. | `testing_strategy.md` | ✅ **DONE** |
| **Phase 2: Core API & Agent** | Configuration | Implement Pydantic `Config` class for environment variables. | `coding_standards.md` | TBD |
| | FastAPI Application | Implement FastAPI app with `/api/health` and `/api/chat` endpoints. | `api_endpoints.md` | TBD |
| | Agent Factory & Orchestrator | Implement `OllamaAgentFactory` and `MultiAgentOrchestrator` service. | `agentic_architecture.md` | TBD |
| | Unit Tests (Core) | Implement unit tests for configuration, API logic, and the agent factory. | `testing_strategy.md` | TBD |
| **Phase 3: Multi-Agent Implementation** | Manager Agent | Implement the main `ManagerAgent` within the orchestrator. | `agentic_architecture.md` | TBD |
| | Web Surfer Worker | Create the `WebSurferAgent` and associated web search/scrape tools. | `agentic_architecture.md`, `coding_standards.md` | TBD |
| | Multi-Agent Integration | Integrate the `WebSurferAgent` as a `ManagedAgent` into the `ManagerAgent`. | `agentic_architecture.md` | TBD |
| | Tool Unit Tests | Implement unit tests for all agent tools, verifying success and error cases. | `testing_strategy.md` | TBD |
| **Phase 4: Conversation & Deployment** | Chat Session Management | Implement `conversation_id` caching in the `MultiAgentOrchestrator`. | `agentic_architecture.md` | TBD |
| | Memory Management | Implement `step_callbacks` for memory pruning and logging. | `agentic_architecture.md` | TBD |
| | Integration Tests | Develop integration tests for multi-agent delegation and chat session persistence. | `testing_strategy.md` | TBD |
| | Production Dockerfile | Create `docker-compose.prod.yml` and production-ready `Dockerfile`. | `production_deployment.md` | TBD | 