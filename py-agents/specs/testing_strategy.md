# Python Testing Strategy Specification

## 1. Purpose

This document outlines the testing strategy for the Orca Agents Python backend. The goal is to ensure the reliability, correctness, and performance of the API through a multi-layered testing approach.

## 2. Testing Framework

-   **Framework:** **`pytest`** will be used as the primary framework for writing and running all tests.
-   **HTTP Client:** The **`httpx`** library will be used within tests to make asynchronous requests to the FastAPI application.
-   **Test Runner:** Tests will be executed via a `Makefile` command (e.g., `make test`).

## 3. Test Types

### 3.1. Unit Tests

-   **Scope:** Focus on testing individual functions and classes in isolation.
-   **Examples:**
    -   Testing Pydantic model validation logic.
    -   Testing utility functions.
    -   Testing the logic within service-layer components.
-   **Mocks:** External dependencies, especially the Ollama service, will be mocked using `pytest-mock` to ensure that unit tests are fast and self-contained.

### 3.2. Integration Tests

-   **Scope:** Focus on testing the interaction between different components of the system.
-   **Environment:** Integration tests will run against a live, containerized instance of the API, which in turn communicates with a real Ollama container. This provides a test environment that closely mirrors production.
-   **Examples:**
    -   Sending a request to the `POST /api/chat` endpoint and verifying that a valid, streamed response is received from the connected Ollama service.
    -   Testing error handling when the Ollama service is unavailable or returns an error.

## 4. Test Organization

-   **Location:** All tests will be located in a top-level `tests/` directory within the `py-agents` project.
-   **Structure:** The `tests/` directory will mirror the structure of the `src/` directory.
    -   `tests/unit/`: Contains all unit tests.
    -   `tests/integration/`: Contains all integration tests.
-   **Fixtures:** Reusable test setup code, such as creating an `httpx` client instance, will be managed using `pytest` fixtures in `tests/conftest.py`.

## 5. Continuous Integration (CI)

-   **Automation:** The test suite will be run automatically on every push and pull request using a CI pipeline (e.g., GitHub Actions).
-   **Pipeline Steps:**
    1.  Set up the Python environment using `uv`.
    2.  Run the linter (`make lint`).
    3.  Build and start the Docker containers (`make up`).
    4.  Run the tests (`make test`).
    5.  Report the test results and coverage. 