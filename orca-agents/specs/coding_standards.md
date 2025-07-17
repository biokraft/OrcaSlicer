# Python Coding Standards

## 1. Purpose

This document defines the coding standards and practices for the Python backend of Orca Agents. Adhering to these standards ensures code quality, consistency, and maintainability.

## 2. Code Formatting & Linting

- **Linter & Formatter**: We use `Ruff` for both linting and formatting. It should be configured in `pyproject.toml`.
- **Configuration**: The `ruff` configuration will enforce a line length of 88 characters and follow the Black formatting style.
- **Pre-commit**: A `pre-commit` hook should be configured to run `ruff` on every commit to automatically format code and report linting errors.

## 3. Configuration Management

- **Pydantic Settings**: All application configuration (environment variables) must be managed through a Pydantic `BaseSettings` class. This provides centralized, type-safe, and validated configuration.
- **Model**: The configuration class should be located in a `config.py` module and include fields for Ollama settings and model names.

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    # Model configuration
    primary_model: str = Field(default="ollama/qwen3:0.6b", description="Fast model for the orchestrator (Manager) agent")
    reasoning_model: str = Field(default="ollama/qwen3:8b", description="Powerful model for the specialist (Worker) agents")

    # Service URLs
    chat_ollama_url: str = Field(default="http://ollama-chat:11434", description="URL for the chat model Ollama service")
    reasoning_ollama_url: str = Field(default="http://ollama-reasoning:11434", description="URL for the reasoning model Ollama service")
```

## 4. Type Hinting

- **Requirement**: All functions and methods must include type hints for their arguments and return values.
- **Pydantic**: We use Pydantic V2 for defining all data structures and API schemas. This ensures data validation and serialization are handled robustly.

## 5. Agent & Tool Development

All agent and tool implementations must follow the patterns outlined in the [Agentic Architecture Specification](agentic_architecture.md). Key patterns include:

- **`OllamaAgentFactory`**: A factory class should be used to create and configure all agent instances, ensuring consistent integration with the Ollama service.
- **`MultiAgentOrchestrator`**: A service class that implements the manager-worker pattern and handles agent caching.
- **Descriptive Docstrings**: Every tool must have a comprehensive docstring explaining its function, arguments, and return value.
- **Clear Error Handling**: Tools must raise descriptive `ValueError` exceptions on failure.

## 6. Service Health

- **Health Check Endpoint**: The FastAPI application must expose a `/api/health` endpoint.
- **Implementation**: This endpoint should perform a basic check to confirm connectivity with **both** Ollama services (e.g., by listing available models from each). This ensures the application reports as unhealthy if either of its core dependencies is down.

## 7. Naming Conventions

- **Variables & Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Modules**: `snake_case`

## 8. Logging

- Standard `logging` module should be used for application-level logging.
- `print()` statements are acceptable within agent tools for providing step-by-step information to the LLM, as described in the `smolagents` guidelines. 