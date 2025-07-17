# Agentic Architecture Specification

## 1. Purpose

This document outlines the agent-based architecture for the Orca Agents backend, based on the `smolagents` library. It details the multi-agent design pattern, LLM integration, memory management, and tool development principles that will guide the implementation.

## 2. Core `smolagents` Integration Pattern

The integration with `smolagents` and Ollama will be centralized through two main components: an agent factory and an orchestrator service.

### `OllamaAgentFactory`

- A factory class responsible for creating and configuring `smolagents` instances (`CodeAgent`, `ToolCallingAgent`).
- It will be initialized with the base URLs for both the chat and reasoning Ollama services.
- It will wrap `smolagents.LiteLLMModel` and connect to the appropriate Ollama instance based on which agent is being created (Manager or Worker).

### `AgentService` / `MultiAgentOrchestrator`

- A high-level service that manages the lifecycle of agents.
- It will implement the **Manager-Worker** pattern.
- It will handle per-chat caching of agent instances to maintain conversation state efficiently, using a `conversation_id`.

## 3. Multi-Agent "Manager-Worker" Architecture

We will adopt a hierarchical manager/worker pattern, with each type of agent connected to a dedicated Ollama instance for optimal performance.

- **Manager Agent**:
    - **Type**: `smolagents.CodeAgent`
    - **Model**: A smaller, faster model (e.g., `ollama/qwen3:0.6b`), configurable via `PRIMARY_MODEL` env var.
    - **Connection**: Connects to the `ollama-chat` service.
    - **Role**: As the orchestrator, this agent's primary role is fast, efficient task delegation. It understands the user's goal and routes sub-tasks to the appropriate specialized worker agents.
- **Worker Agents**:
    - **Type**: `smolagents.ToolCallingAgent` wrapped in `smolagents.ManagedAgent`.
    - **Model**: A powerful reasoning model (`ollama/qwen3:8b`), configurable via `REASONING_MODEL` env var.
    - **Connection**: Connects to the `ollama-reasoning` service.
    - **Role**: Each worker is a specialist. It uses the powerful reasoning model to execute complex tasks requiring deep understanding, such as web analysis or code generation.

### Example: Web Surfing Delegation

1. **`ManagerAgent`**: Receives a high-level task: "Research the latest advancements in AI."
2. The `ManagerAgent` determines that this requires web access and invokes the `web_searcher` managed agent.
3. **`WebSurferAgent` (Worker)**:
    - A `ManagedAgent` named `web_searcher` with the description: "Searches the web for current information and provides summaries."
    - It is equipped with `DuckDuckGoSearchTool` and a web scraping tool.
    - It executes the search, scrapes relevant content, and returns a summary to the `ManagerAgent`.
4. The `ManagerAgent` synthesizes the results and presents the final answer.

## 4. Conversational Memory Management

- **Stateful Conversations**: The `AgentService` will use a `conversation_id` to retrieve or create cached agent instances. The `agent.run()` method will be called with `reset=False` to maintain context within a session.
- **Memory Pruning**: To prevent context overflow in long conversations, a `step_callbacks` function will be attached to each agent instance. This callback will log agent steps for debugging and can be extended to implement memory pruning strategies (e.g., keeping the first message and the last N turns).

## 5. Tool Implementation Standards

All tools must adhere to the following:

- **Descriptive Docstrings**: The docstring is the API for the LLM. It must clearly describe the tool's purpose, arguments (including data types and format), and what it returns.
- **Informative Logging**: Use `print()` to log key actions for observability.
- **Robust Error Handling**: If a tool fails, it must raise a `ValueError` with a clear, descriptive message that helps the agent understand the error and correct its inputs. 