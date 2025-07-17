# API Endpoints Specification

## 1. Purpose

This document provides a detailed specification for all API endpoints exposed by the Orca Agents backend. It includes routes, request/response schemas, and status codes.

## 2. General Principles

-   **Base URL:** All API routes are prefixed with `/api`.
-   **Authentication:** No authentication is required, as the API is only exposed to the local machine and is intended for communication with the OrcaSlicer GUI.
-   **Error Handling:** The API will return standard HTTP status codes and a JSON response body with an `error` key for failed requests.

## 3. Core Endpoints

### 3.1. Health Check

-   **Route:** `GET /api/health`
-   **Description:** A simple endpoint to verify that the API server is running and accessible.
-   **Success Response:**
    -   **Code:** `200 OK`
    -   **Body:** `{"status": "ok"}`

### 3.2. Chat Interaction

-   **Route:** `POST /api/chat`
-   **Description:** The primary endpoint for handling chat interactions. It receives a user's query and streams back the AI's response.
-   **Request Body:**

    ```json
    {
      "message": "Why is my first layer not sticking to the bed?",
      "model": "qwen3-8b",
      "stream": true,
      "options": {
        "temperature": 0.8
      }
    }
    ```

    -   **`message` (str, required):** The user's query.
    -   **`model` (str, optional):** The specific Qwen3 model to use. If omitted, the backend's default model is used.
    -   **`stream` (bool, optional):** Whether to stream the response. Defaults to `true`.
    -   **`options` (dict, optional):** A dictionary of Ollama-specific parameters to pass to the model.

-   **Success Response (Streaming):**
    -   **Code:** `200 OK`
    -   **Content-Type:** `text/event-stream`
    -   **Body:** A stream of JSON objects, where each object represents a token from the model's response, following the Ollama streaming API format.
        ```json
        {"token": "The", "done": false}
        {"token": " first", "done": false}
        {"token": " layer...", "done": false}
        {"done": true}
        ```

-   **Success Response (Non-Streaming):**
    -   **Code:** `200 OK`
    -   **Content-Type:** `application/json`
    -   **Body:** A single JSON object containing the full response.
        ```json
        {"response": "The first layer..."}
        ```

-   **Error Responses:**
    -   **Code:** `422 Unprocessable Entity` (if the request body is invalid).
    -   **Code:** `500 Internal Server Error` (if the backend fails to communicate with Ollama).

## 4. Pydantic Models

The request and response schemas will be enforced using Pydantic models to ensure type safety and automatic validation. These models will be defined in a dedicated `api.schemas` module. 