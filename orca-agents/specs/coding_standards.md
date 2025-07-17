# Python Coding Standards

## 1. Purpose

This document defines the coding standards and practices for the Python backend of Orca Agents. Adhering to these standards ensures code quality, consistency, and maintainability.

## 2. Code Formatting & Linting

- **Linter & Formatter**: We use `Ruff` for both linting and formatting. It should be configured in `pyproject.toml`.
- **Configuration**: The `ruff` configuration will enforce a line length of 88 characters and follow the Black formatting style.
- **Pre-commit**: A `pre-commit` hook should be configured to run `ruff` on every commit to automatically format code and report linting errors.

## 3. Type Hinting

- **Requirement**: All functions and methods must include type hints for their arguments and return values.
- **Pydantic**: We use Pydantic V2 for defining all data structures and API schemas. This ensures data validation and serialization are handled robustly.

## 4. Agent & Tool Development

All agent and tool implementations must follow the principles outlined in the [Agentic Architecture Specification](agentic_architecture.md). Key requirements include:

- **Descriptive Docstrings**: Every tool must have a comprehensive docstring explaining its function, arguments, and return value.
- **Clear Error Handling**: Tools must raise descriptive `ValueError` exceptions on failure.
- **Agent Simplicity**: Keep agents focused on specific tasks, following the manager/worker pattern.

## 5. Naming Conventions

- **Variables & Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Modules**: `snake_case`

## 6. Logging

- Standard `logging` module should be used for application-level logging.
- `print()` statements are acceptable within agent tools for providing step-by-step information to the LLM, as described in the `smolagents` guidelines. 