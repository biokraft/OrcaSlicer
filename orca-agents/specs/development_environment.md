# Development Environment Specification

## 1. Purpose

This document provides a comprehensive guide for setting up and managing a local development environment for the Orca Agents backend. The goal is to ensure a consistent and efficient workflow for all contributors.

## 2. Core Tools

-   **Package Manager:** **`uv`** is the sole tool for managing Python dependencies and virtual environments.
-   **Containerization:** **Docker** and **Docker Compose** are used to run the application and its services (`api`, `ollama`, `ollama-init`).
-   **Task Runner:** A **`Makefile`** provides a set of convenient commands for common development tasks.

## 3. Initial Setup

1.  **Clone the Repository**.
2.  **Install `uv` and Docker**.
3.  **Configure Environment Variables**:
    -   Create a file named `.env` in the project root.
    -   Copy the contents of `.env.example` into it.
    -   Modify the `.env` file to select the desired LLM models for local development. For example:
        ```env
        # .env
        PRIMARY_MODEL=ollama/qwen3:0.6b
        REASONING_MODEL=ollama/qwen:7b
        ```
4.  **Build and Start Services**:
    ```bash
    make up
    ```
    This single command will:
    -   Build the `api` Docker image.
    -   Start the `ollama` service.
    -   Run the `ollama-init` service to pull the models defined in your `.env` file.
    -   Start the `api` service with hot-reloading.

## 4. `pyproject.toml` Structure

The `pyproject.toml` file is the central configuration file for Python dependencies.

-   **`[project]`:** Defines project metadata and `dependencies`.
-   **`[project.optional-dependencies]`:**
    -   `dev`: Specifies development-only dependencies like `pytest` and `ruff`.
-   **`[tool.ruff]`:** Configures the `ruff` linter and formatter.

To install dependencies locally (e.g., for IDE integration), create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate
uv sync --all-extras
```

## 5. Development Workflow with Docker

The primary development workflow is container-based to ensure consistency with production.

### 5.1. Running the Backend

-   **Command:** `make up`
-   **Action:** Runs `docker-compose up --build`. This starts all services. The `api` service volume-mounts the source code, enabling hot-reloading on code changes.

### 5.2. Stopping the Backend

-   **Command:** `make down`
-   **Action:** Stops and removes the running containers.

### 5.3. Managing Dependencies

-   **Adding:** `uv add <package-name>`
-   **Removing:** `uv remove <package-name>`
-   **Updating `pyproject.toml`**: After modifying dependencies, they are automatically synced within the container on the next `make up`. For your local environment, run `uv sync --all-extras`.

### 5.4. Running Tests

-   **Command:** `make test`
-   **Action:** Executes the `pytest` suite inside the `api` container.

### 5.5. Linting and Formatting

-   **Linting:** `make lint` (runs `ruff check`)
-   **Formatting:** `make format` (runs `ruff format`)
-   Both commands are executed inside the `api` container. 