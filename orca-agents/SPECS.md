# Orca Agents Backend Specifications

## 1. Project Overview

This project, codenamed "Orca Agents," provides the containerized Python backend for the AI Assistant in OrcaSlicer. It is a self-contained system responsible for serving the AI model, handling chat logic, and providing a clear API for the main OrcaSlicer application. It is built with FastAPI, managed with Docker, and uses `uv` for package management.

## 2. Specification Library

| File | Description |
|---|---|
| `specs/architecture.md` | The containerized backend architecture, including FastAPI, Ollama, and Docker. |
| `specs/development_environment.md` | Guide for setting up a local development environment using `uv` and Docker. |
| `specs/api_endpoints.md` | Detailed specification for all API endpoints, including request/response schemas. |
| `specs/testing_strategy.md` | The strategy for testing the Python backend, including unit and integration tests. |
| `specs/coding_standards.md` | Code style and linting rules for the Python codebase. |

## 3. Implementation Plan

| Phase | Focus Area | Key Deliverables | Related Specs | Status |
|---|---|---|---|---|
| **Phase 1: Foundation** | Project Scaffolding | Create `pyproject.toml` and initial directory structure. | `development_environment.md` | TBD |
| | Dev Environment | Configure `uv` and `Makefile` for easy setup. | `development_environment.md` | TBD |
| | Docker Setup | Create `Dockerfile.api` and `docker-compose.yml`. | `architecture.md` | TBD |
| **Phase 2: Core API** | FastAPI Application | Basic FastAPI app with a health check endpoint. | `api_endpoints.md` | TBD |
| | Chat Endpoint | Implement `/api/chat` endpoint with Pydantic models. | `api_endpoints.md` | TBD |
| | Ollama Integration | Connect to Ollama service and stream a basic response. | `architecture.md` | TBD |
| **Phase 3: Testing & Refinement** | Unit Tests | Implement unit tests for API logic using `pytest`. | `testing_strategy.md` | TBD |
| | Linting Setup | Configure `ruff` and enforce code style. | `coding_standards.md` | TBD |
| | Configuration | Manage settings (e.g., Ollama URL) via environment variables. | `architecture.md` | TBD | 