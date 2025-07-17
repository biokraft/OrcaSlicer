# API Endpoints Specification

## 1. Purpose

This document provides a detailed specification for all API endpoints in the Orca Agents backend. It defines the request/response schemas and the expected behavior for each endpoint.

## 2. Base URL

The API will be served under the `/api` prefix.

## 3. Endpoints

### 3.1 Health Check

- **Endpoint**: `GET /api/health`
- **Description**: A simple endpoint to verify that the API service is running and healthy.
- **Request Body**: None.
- **Success Response (200 OK)**:
  ```json
  {
    "status": "ok"
  }
  ```

### 3.2 Chat Endpoint

- **Endpoint**: `POST /api/chat`
- **Description**: The primary endpoint for interacting with the AI agent. It accepts a user's message and optionally a conversation ID to maintain state. The underlying agentic logic, including memory management and tool use, is detailed in the [Agentic Architecture Specification](agentic_architecture.md).
- **Request Body**: `ChatRequest`
  ```python
  from pydantic import BaseModel, Field
  from typing import Optional

  class ChatRequest(BaseModel):
      """
      Represents a user's message to the chat endpoint.
      """
      message: str = Field(..., description="The user's message or query.")
      conversation_id: Optional[str] = Field(None, description="An optional ID to maintain conversational context.")
  ```
- **Success Response (200 OK)**: `ChatResponse`
  - The response will be a streaming response (`StreamingResponse`) that yields chunks of a JSON object. The client will need to assemble these chunks. Each chunk is a part of the `ChatResponse` model.
  ```python
  from pydantic import BaseModel, Field

  class ChatResponse(BaseModel):
      """
      Represents the agent's response to a user's message.
      """
      reply: str = Field(..., description="The agent's text response.")
      conversation_id: str = Field(..., description="The ID for the current conversation, to be used in subsequent requests.")
  ```

## 4. Error Handling

- **4xx Client Errors**: If the request is invalid (e.g., missing fields, incorrect types), the API will return a `422 Unprocessable Entity` response with a detailed JSON body explaining the validation errors.
- **5xx Server Errors**: If an unexpected error occurs on the server (e.g., cannot connect to Ollama, unhandled exception in an agent tool), the API will return a `500 Internal Server Error` response with a generic error message. 