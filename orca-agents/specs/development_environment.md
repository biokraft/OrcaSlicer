# Development Environment Specification

## 1. Purpose

This document provides a comprehensive guide for setting up and managing a local development environment for the Orca Agents backend. The goal is to ensure a consistent and efficient workflow for all contributors.

## 2. Core Tools

-   **Package Manager:** **`uv`** is the sole tool for managing Python dependencies and virtual environments.
-   **Containerization:** **Docker** and **Docker Compose** are used to run the application and its services.
-   **Task Runner:** A **`Makefile`** provides a set of convenient commands for common development tasks.

## 3. Initial Setup

1.  **Clone the Repository:** Obtain the source code from the project repository.
2.  **Install `uv`:** Follow the official `uv` installation instructions for your operating system.
3.  **Create a Virtual Environment:** From the `py-agents` directory, run:
    ```bash
    uv venv
    ```
    This creates a `.venv` directory.
4.  **Activate the Environment:**
    -   **Linux/macOS:** `source .venv/bin/activate`
    -   **Windows:** `.venv\Scripts\activate`
5.  **Install Dependencies:**
    ```bash
    uv sync
    ```
    This command installs all dependencies listed in `pyproject.toml` into the virtual environment.

## 4. `pyproject.toml` Structure

The `pyproject.toml` file is the central configuration file.

-   **`[project]`:** Defines project metadata like `name`, `version`, and `dependencies`.
-   **`[project.optional-dependencies]`:**
    -   `dev`: Specifies development-only dependencies, such as `pytest` and `ruff`.
-   **`[tool.uv.sources]`:** (If needed) Specifies any private package indexes.
-   **`[tool.ruff]`:** Configures the `ruff` linter and formatter.

To install development dependencies, a developer would run `uv sync --all-extras`.

## 5. Development Workflow

### 5.1. Running the Backend

-   **Command:** `make up`
-   **Action:** Starts the `api` and `ollama` services using `docker-compose up`. The `api` service will be configured with hot-reloading, so any changes to the Python code will automatically restart the server.

### 5.2. Managing Dependencies

-   **Adding a dependency:** `uv add <package-name>`
-   **Adding a dev dependency:** `uv add --dev <package-name>`
-   **Removing a dependency:** `uv remove <package-name>`
-   **Syncing the environment:** `uv sync` (or `uv sync --all-extras` for dev)

### 5.3. Running Tests

-   **Command:** `make test`
-   **Action:** Executes the `pytest` test suite against the running API container to ensure a production-like testing environment.

### 5.4. Linting and Formatting

-   **Command:** `make lint`
-   **Action:** Runs `ruff check` to identify and report any code style violations.
-   **Command:** `make format`
-   **Action:** Runs `ruff format` to automatically format the codebase according to the configured rules. 