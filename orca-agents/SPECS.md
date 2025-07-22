# Orca Agents Backend Specifications

## 1. Project Overview

This project, codenamed "Orca Agents," provides the containerized Python backend for the AI Assistant in OrcaSlicer. It is a self-contained system responsible for serving AI models, handling multi-agent chat logic, and providing a clear API for the main OrcaSlicer application.

**Current Status**: **Phase 3 Complete** - Full multi-agent system with manager-worker delegation pattern

**Technology Stack**:
- **Framework**: FastAPI with `smolagents` for multi-agent orchestration
- **LLM Backend**: Dual Ollama architecture (chat + reasoning models)
- **Package Management**: `uv` for fast Python dependency management
- **Containerization**: Docker with docker-compose orchestration
- **Testing**: pytest with comprehensive unit + integration test suite

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

**Phase 1-3 Foundation Complete:**
- ✅ **Dual Ollama Architecture**: Chat service (qwen3:0.6b) + Reasoning service (qwen3:8b)
- ✅ **Multi-Agent Infrastructure**: `OllamaAgentFactory`, `MultiAgentOrchestrator` with conversation management
- ✅ **FastAPI Application**: Full API with health checks, chat endpoints, and conversation management
- ✅ **Development Environment**: UV, ruff, pre-commit, comprehensive Makefile, Docker setup
- ✅ **Configuration Management**: Pydantic settings with dual Ollama URLs and agent parameters
- ✅ **Multi-Agent System**: Manager-worker delegation with CodeAgent (reasoning) + ToolCallingAgent (web search)
- ✅ **Comprehensive Testing**: 55 unit + integration tests with 92-93% coverage for core agent modules

**Current Implementation Notes:**
- **Multi-Agent Architecture**: Manager-worker delegation pattern using smolagents framework
  - **Manager Agent**: `CodeAgent` on reasoning model (qwen3:8b) for intelligent task orchestration
  - **Web Worker**: `ToolCallingAgent` on chat model (qwen3:0.6b) with DuckDuckGo search + webpage tools
  - **Delegation Logic**: Automatic worker selection based on task requirements
- **Conversation Management**: Context preservation across agent switches with memory pruning
- **Testing Coverage**: 55 tests (22 factory + 25 orchestrator + 8 integration) with comprehensive workflows
- **Error Handling**: Graceful fallbacks when tools unavailable or multi-agent setup fails
- **Production Ready**: Dual Ollama architecture with proper configuration management
- **Phase 3 Complete**: Ready for Phase 4 conversation persistence and deployment features

## 2.2. System Capabilities Overview

**Multi-Agent Architecture:**
- **Manager Agent**: Intelligent task orchestration using CodeAgent on qwen3:8b
- **Web Surfer Worker**: Specialized web browsing with DuckDuckGo search + webpage visiting
- **Agent Delegation**: Automatic task routing based on user intent and requirements
- **Context Management**: Conversation continuity across agent switches

**Conversation Management:**
- **Session Tracking**: Conversation ID-based caching with statistics and lifecycle management
- **Memory Pruning**: Step callbacks for efficient long-conversation handling
- **Reset Logic**: Smart context preservation vs. fresh conversation detection

**Error Handling & Resilience:**
- **Graceful Fallbacks**: Simple chat mode when multi-agent setup fails
- **Tool Availability**: Dynamic handling of missing dependencies (e.g., web search tools)
- **LLM Connectivity**: Robust error handling for Ollama service unavailability

**Testing & Quality:**
- **55 Test Suite**: Comprehensive unit + integration tests covering all workflows
- **92-93% Coverage**: High coverage for core agent modules (factory + orchestrator)
- **CI/CD Ready**: Automated testing with lint, format, and coverage checks

**Production Features:**
- **Dual Ollama Setup**: Separate services for chat vs. reasoning tasks
- **Docker Integration**: Full containerization with docker-compose orchestration
- **Configuration Management**: Pydantic settings with environment variable support
- **API Endpoints**: FastAPI with health checks and chat functionality

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
| | Unit Tests (Core) | Implement unit tests for configuration, API logic, and the agent factory. | `testing_strategy.md` | ✅ **DONE** |
| **Phase 3: Multi-Agent Implementation** | Manager Agent | Implement the main `ManagerAgent` within the orchestrator. | `agentic_architecture.md` | ✅ **DONE** |
| | Web Surfer Worker | Create the `WebSurferAgent` and associated web search/scrape tools. | `agentic_architecture.md`, `coding_standards.md` | ✅ **DONE** |
| | Multi-Agent Integration | Integrate the `WebSurferAgent` as a `ManagedAgent` into the `ManagerAgent`. | `agentic_architecture.md` | ✅ **DONE** |
| | Tool Unit Tests | Implement unit tests for all agent tools, verifying success and error cases. | `testing_strategy.md` | ✅ **DONE** |
| **Phase 4: Conversation & Deployment** | Chat Session Management | Implement `conversation_id` caching in the `MultiAgentOrchestrator`. | `agentic_architecture.md` | ✅ **DONE** |
| | Memory Management | Implement `step_callbacks` for memory pruning and logging. | `agentic_architecture.md` | ✅ **DONE** |
| | Integration Tests | Develop integration tests for multi-agent delegation and chat session persistence. | `testing_strategy.md` | ✅ **DONE** |
| | **Note**: Phase 4 features were implemented during Phase 3 as part of multi-agent system requirements. | | | |
| **Phase 5: Database Persistence** | Database Setup | Configure SQLite, SQLAlchemy, and Alembic for migrations. | `database_persistence.md` | TBD |
| | Models & Schemas | Implement Pydantic-based SQLAlchemy models for `Conversation` and `Message`. | `database_persistence.md` | TBD |
| | Persistence Service | Create a service to handle saving and retrieving chat history. | `database_persistence.md` | TBD |
| | API Integration | Add new endpoints (`/api/conversations`, `/api/conversations/{id}`) and integrate into chat logic. | `database_persistence.md`, `api_endpoints.md` | TBD |
| | Database Unit Tests | Write unit tests for the database models and persistence service. | `testing_strategy.md` | TBD |
| **Phase 6: UI Integration** | Chat History UI | Design and implement the UI for browsing and loading past conversations. | `database_persistence.md` | TBD |
