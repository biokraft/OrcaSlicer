# Python Testing Strategy

## 1. Purpose

This document outlines the testing strategy for the Python backend of Orca Agents. The goal is to ensure the reliability, correctness, and robustness of the API and the underlying agentic system.

## 2. Testing Framework

- **Framework**: We will use `pytest` as the primary testing framework.
- **Runner**: Tests will be executed via `uv run pytest`.

## 3. Test Types

### 3.1 Unit Tests

- **Scope**: Unit tests will focus on individual components in isolation.
- **Targets**:
    - **API Logic**: Test the logic within API endpoint functions, such as request validation and response formatting.
    - **Tools**: Each agent tool must have dedicated unit tests to verify its functionality. This includes testing both successful execution and the raising of descriptive `ValueError` exceptions for invalid inputs.
    - **Utility Functions**: Any helper or utility functions should be covered by unit tests.
- **Mocking**: External services, like the Ollama API and agent LLM calls, will be heavily mocked to ensure tests are fast and deterministic.

### 3.2 Integration Tests

- **Scope**: Integration tests will verify the interaction between different components of the system.
- **Targets**:
    - **API and Agent Interaction**: Test the full flow from receiving a request at the `/api/chat` endpoint to invoking the agent system and returning a response.
    - **Multi-Agent Communication**: Verify that the Manager Agent correctly delegates tasks to Worker Agents. This will involve mocking the LLM responses to control the agent's behavior and asserting that the correct worker is called.
    - **Memory Management**: Test the conversational memory system, ensuring that context is maintained when a `conversation_id` is provided and that memory pruning callbacks function as expected.

## 4. Test Organization

- All tests will be located in the `tests/` directory.
- The directory structure within `tests/` will mirror the application's source code structure (e.g., `tests/tools/` for tool tests).

## 5. Continuous Integration (CI)

- All tests will be run automatically in a CI pipeline on every push and pull request to the main branch.
- The pipeline will also run the `ruff` linter and formatter to ensure code quality. 