# Python Coding Standards Specification

## 1. Purpose

This document defines the coding standards, formatting guidelines, and linting rules for the Orca Agents Python project. Adherence to these standards is mandatory to ensure code quality, readability, and consistency across the codebase.

## 2. Formatter and Linter

-   **Tool:** **`Ruff`** will be used as the all-in-one tool for formatting and linting. It is chosen for its exceptional performance and comprehensive feature set.
-   **Configuration:** All `Ruff` rules and settings will be defined in the `[tool.ruff]` section of the `pyproject.toml` file.

### 2.1. Formatting

-   **Enforcement:** Code will be formatted according to the rules configured in `[tool.ruff.format]`.
-   **Line Length:** The maximum line length will be set to 88 characters to align with common Python standards (e.g., Black).
-   **Workflow:** Developers should run `make format` or configure their IDE to format on save. The CI pipeline will fail if unformatted code is pushed.

### 2.2. Linting

-   **Rule Set:** The linter will be configured with a curated set of rules from `Ruff`'s extensive library, including:
    -   `pycodestyle` (E) and `pyflakes` (F) for basic error checking.
    -   `isort` (I) for import sorting.
    -   `flake8-bugbear` (B) for finding potential bugs.
    -   `flake8-annotations` (ANN) for enforcing type hint usage.
-   **Workflow:** Developers should run `make lint` to check for violations. The CI pipeline will enforce this as a required check.

## 3. Naming Conventions

-   **Modules:** `lower_case_with_underscores`.
-   **Classes:** `PascalCase`.
-   **Functions & Variables:** `lower_case_with_underscores`.
-   **Constants:** `UPPER_CASE_WITH_UNDERSCORES`.

## 4. Type Hinting

-   **Requirement:** All function signatures and class attributes must include type hints.
-   **Style:** Use modern type hinting syntax (e.g., `list[str]` instead of `List[str]`).
-   **Enforcement:** The `flake8-annotations` linting rule (`ANN`) will be enabled to enforce the presence of type hints.

## 5. Docstrings

-   **Requirement:** All public modules, functions, classes, and methods must have a docstring.
-   **Format:** Docstrings should follow the [**Google Python Style Guide**](https://google.github.io/styleguide/pyguide.html#3.8-comments-and-docstrings).
    ```python
    """A brief summary of the function.

    Args:
        arg1 (str): Description of the first argument.
        arg2 (int): Description of the second argument.

    Returns:
        bool: Description of the return value.
    """
    ```

## 6. Logging

-   **Library:** The standard Python `logging` module will be used for all application logging.
-   **Configuration:** Logging will be configured in the main application entrypoint to ensure consistent formatting and output.
-   **Usage:** Libraries and sub-modules should get a logger instance via `logging.getLogger(__name__)`. 