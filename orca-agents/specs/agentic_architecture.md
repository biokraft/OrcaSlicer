# Agentic Architecture Specification

## 1. Purpose

This document outlines the agent-based architecture for the Orca Agents backend, based on the `smolagents` library. It details the multi-agent design pattern, LLM integration, memory management, and tool development principles that will guide the implementation.

## 2. Core Principles

The agent system is built on the following principles from the `smolagents` framework:

- **Simplicity**: Agents should be as simple as possible. We will prefer deterministic code over LLM calls for simple logic and group related tool calls into single, more powerful tools.
- **Clear Information Flow**: The reliability of the system depends on providing clear, unambiguous information to the LLM. This will be achieved through explicit task formulation and highly descriptive tool documentation.

## 3. Multi-Agent Architecture

We will adopt a hierarchical manager/worker pattern to separate concerns and improve robustness.

- **Manager Agent**: A high-level `smolagents.CodeAgent` that understands the user's overall goal. It will be equipped with a more powerful reasoning model (e.g., `qwen:7b`). Its primary role is to delegate tasks to specialized worker agents.
- **Worker Agents**: Specialized `smolagents.ToolCallingAgent` instances, each responsible for a specific domain (e.g., web browsing, file system operations). They will use smaller, faster models (e.g., `qwen:0.5b`) and will be wrapped in `smolagents.ManagedAgent` to be exposed as "tools" to the Manager Agent.

### Example: Web Browsing System

- **`ManagerAgent`**: Receives a high-level task like "Research the benefits of..."
- **`WebSurferAgent` (Worker)**: A `ManagedAgent` equipped with `DuckDuckGoSearchTool` and `VisitWebpageTool`. The Manager delegates the "search and scrape" sub-task to this agent.

## 4. LLM Integration

- **`LiteLLMModel`**: We will use the `smolagents.LiteLLMModel` class as the universal adapter for all LLMs.
- **Local Development**: For local development and testing, we will connect to a local Ollama server running models like `qwen:0.5b` and `qwen:7b`. This is configured by prefixing the model ID with `ollama/`, e.g., `ollama/qwen:7b`.
- **Flexibility**: This approach allows for easy swapping between local models and more powerful cloud models (e.g., from Groq or Anthropic) without changing the core agent logic.

## 5. Conversational Memory Management

To support stateful conversations in the `/api/chat` endpoint, we will implement the following:

- **History Persistence**: The `agent.run()` method will be called with `reset=False` for subsequent turns in a single conversation to maintain context. A session or conversation ID will be used to track conversation state.
- **Memory Pruning**: For long-running conversations, we will implement a `step_callbacks` function to prevent the context window from overflowing. This callback will prune the agent's memory, keeping the initial task and the most recent N steps.

## 6. Tool Implementation Standards

All tools developed for agents must adhere to the following standards:

- **Descriptive Docstrings**: A tool's docstring is its API for the LLM. It must clearly describe what the tool does, all of its arguments (including format), and its return value.
- **Informative Logging**: Tools should use `print()` statements to log important intermediate steps.
- **Descriptive Errors**: If a tool fails, it must raise a `ValueError` with a precise message explaining what went wrong and how the agent can correct its inputs. 