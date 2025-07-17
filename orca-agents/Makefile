# Makefile for Orca Agents
# Best practices: variables, error handling, proper phony targets

# Variables
SHELL := /bin/bash
.DEFAULT_GOAL := help
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Project configuration
PROJECT_NAME := orca-agents
PYTHON_VERSION := 3.13
DOCKER_COMPOSE := docker-compose
UV := uv

# Docker configuration
API_SERVICE := api
OLLAMA_CHAT_SERVICE := ollama-chat
OLLAMA_REASONING_SERVICE := ollama-reasoning
OLLAMA_INIT_SERVICE := ollama-init
CHAT_MODEL := qwen3:0.6b
REASONING_MODEL := qwen3:8b

# Test configuration
PYTEST_ARGS := -q --disable-warnings --tb=short --no-cov --junitxml=report.xml

# Colors for output
RESET := \033[0m
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
CYAN := \033[36m

# Phony targets
.PHONY: help install dev-setup up down restart logs logs-api logs-ollama
.PHONY: logs-ollama-chat logs-ollama-reasoning docker-build
.PHONY: test test-cov lint format check clean
.PHONY: ollama-pull ollama-pull-chat ollama-pull-reasoning ollama-list ollama-models ollama-health
.PHONY: dev docker-clean check-tools
.PHONY: pre-commit-run pre-commit-update

## Help
help: ## Show this help message
	@/bin/echo -e "$(BOLD)$(PROJECT_NAME) - Development Commands$(RESET)"
	@/bin/echo -e ""
	@/bin/echo -e "$(BOLD)Usage:$(RESET)"
	@/bin/echo -e "  make <target>"
	@/bin/echo -e ""
	@/bin/echo -e "$(BOLD)Targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

## Development Environment
install: ## Install Python dependencies
	@/bin/echo -e "$(BLUE)Installing dependencies...$(RESET)"
	$(UV) sync --all-extras
	@/bin/echo -e "$(GREEN)Dependencies installed successfully$(RESET)"

dev-setup: install ## Complete development setup (dependencies + pre-commit)
	@/bin/echo -e "$(BLUE)Setting up development environment...$(RESET)"
	$(UV) run pre-commit install
	@/bin/echo -e "$(GREEN)Development environment ready$(RESET)"

## Docker Operations
up: ## Start all services (API + Ollama)
	@/bin/echo -e "$(BLUE)Starting services...$(RESET)"
	$(DOCKER_COMPOSE) up -d --build
	@/bin/echo -e "$(GREEN)Services started$(RESET)"
	@/bin/echo -e "$(YELLOW)API available at: http://localhost:8001$(RESET)"
	@/bin/echo -e "$(YELLOW)Ollama available at: http://localhost:11434$(RESET)"

down: ## Stop all services
	@/bin/echo -e "$(BLUE)Stopping services...$(RESET)"
	$(DOCKER_COMPOSE) down
	@/bin/echo -e "$(GREEN)Services stopped$(RESET)"

restart: down up ## Restart all services

logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

logs-api: ## Show logs from API service only
	$(DOCKER_COMPOSE) logs -f $(API_SERVICE)

logs-ollama: ## Show logs from both Ollama services
	$(DOCKER_COMPOSE) logs -f $(OLLAMA_CHAT_SERVICE) $(OLLAMA_REASONING_SERVICE)

logs-ollama-chat: ## Show logs from chat Ollama service only
	$(DOCKER_COMPOSE) logs -f $(OLLAMA_CHAT_SERVICE)

logs-ollama-reasoning: ## Show logs from reasoning Ollama service only
	$(DOCKER_COMPOSE) logs -f $(OLLAMA_REASONING_SERVICE)

docker-build: ## Build Docker images without cache
	@/bin/echo -e "$(BLUE)Building Docker images...$(RESET)"
	$(DOCKER_COMPOSE) build --no-cache
	@/bin/echo -e "$(GREEN)Docker images built$(RESET)"

## Testing
test: ## Run tests
	@/bin/echo -e "$(BLUE)Running tests...$(RESET)"
	$(UV) run pytest $(PYTEST_ARGS)

test-cov: ## Run tests with coverage report
	@/bin/echo -e "$(BLUE)Running tests with coverage...$(RESET)"
	$(UV) run pytest --cov=app --cov-report=html --cov-report=term-missing

## Code Quality
lint: ## Run code linting
	@/bin/echo -e "$(BLUE)Running linter...$(RESET)"
	$(UV) run ruff check .

format: ## Format code
	@/bin/echo -e "$(BLUE)Formatting code...$(RESET)"
	$(UV) run ruff format .

check: lint test ## Run all quality checks (lint + test)
	@/bin/echo -e "$(GREEN)All checks passed$(RESET)"

pre-commit-run: ## Run pre-commit on all files
	@/bin/echo -e "$(BLUE)Running pre-commit hooks...$(RESET)"
	$(UV) run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@/bin/echo -e "$(BLUE)Updating pre-commit hooks...$(RESET)"
	$(UV) run pre-commit autoupdate

## Ollama Model Management
ollama-pull: ## Pull models for both Ollama services
	@/bin/echo -e "$(BLUE)Pulling Ollama models...$(RESET)"
	@/bin/echo -e "$(YELLOW)Pulling chat model: $(CHAT_MODEL)$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_CHAT_SERVICE) ollama pull $(CHAT_MODEL)
	@/bin/echo -e "$(YELLOW)Pulling reasoning model: $(REASONING_MODEL)$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_REASONING_SERVICE) ollama pull $(REASONING_MODEL)
	@/bin/echo -e "$(GREEN)Models pulled successfully$(RESET)"

ollama-pull-chat: ## Pull chat model only
	@/bin/echo -e "$(BLUE)Pulling chat model: $(CHAT_MODEL)$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_CHAT_SERVICE) ollama pull $(CHAT_MODEL)

ollama-pull-reasoning: ## Pull reasoning model only
	@/bin/echo -e "$(BLUE)Pulling reasoning model: $(REASONING_MODEL)$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_REASONING_SERVICE) ollama pull $(REASONING_MODEL)

ollama-list: ## List available models in both services
	@/bin/echo -e "$(BLUE)Models in chat service:$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_CHAT_SERVICE) ollama list
	@/bin/echo -e "$(BLUE)Models in reasoning service:$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_REASONING_SERVICE) ollama list

ollama-models: ollama-list ## Alias for ollama-list

ollama-health: ## Check health of both Ollama services
	@/bin/echo -e "$(BLUE)Checking Ollama services health...$(RESET)"
	@curl -sf http://localhost:11434/api/version > /dev/null && /bin/echo -e "$(GREEN)Chat Ollama service: OK$(RESET)" || /bin/echo -e "$(RED)Chat Ollama service: FAILED$(RESET)"
	@curl -sf http://localhost:11435/api/version > /dev/null && /bin/echo -e "$(GREEN)Reasoning Ollama service: OK$(RESET)" || /bin/echo -e "$(RED)Reasoning Ollama service: FAILED$(RESET)"

## Cleanup
clean: ## Clean up Docker resources
	@/bin/echo -e "$(BLUE)Cleaning up...$(RESET)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	@/bin/echo -e "$(GREEN)Cleanup completed$(RESET)"

docker-clean: ## Deep clean Docker (removes all unused resources)
	@/bin/echo -e "$(RED)Warning: This will remove ALL unused Docker resources$(RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -a --volumes -f; \
		/bin/echo -e "$(GREEN)Deep clean completed$(RESET)"; \
	else \
		/bin/echo -e "$(YELLOW)Cancelled$(RESET)"; \
	fi

## Development Shortcuts
dev: up ## Start development environment (alias for 'up')

# Check if required tools are installed
check-tools:
	@which $(UV) > /dev/null || (/bin/echo -e "$(RED)Error: uv is not installed$(RESET)" && exit 1)
	@which docker > /dev/null || (/bin/echo -e "$(RED)Error: docker is not installed$(RESET)" && exit 1)
	@which $(DOCKER_COMPOSE) > /dev/null || (/bin/echo -e "$(RED)Error: docker-compose is not installed$(RESET)" && exit 1)

# Run tool checks before most operations
install dev-setup up: | check-tools
