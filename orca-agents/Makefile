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
OLLAMA_SERVICE := ollama
DEFAULT_MODEL := qwen:0.5b

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
.PHONY: test test-cov lint format check clean
.PHONY: ollama-pull ollama-list ollama-models
.PHONY: dev docker-build docker-clean
.PHONY: pre-commit-run pre-commit-update

## Help
help: ## Show this help message
	@echo "$(BOLD)$(PROJECT_NAME) - Development Commands$(RESET)"
	@echo ""
	@echo "$(BOLD)Usage:$(RESET)"
	@echo "  make <target>"
	@echo ""
	@echo "$(BOLD)Targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

## Development Environment
install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(UV) sync --all-extras
	@echo "$(GREEN)Dependencies installed successfully$(RESET)"

dev-setup: install ## Complete development setup (dependencies + pre-commit)
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	$(UV) run pre-commit install
	@echo "$(GREEN)Development environment ready$(RESET)"

## Docker Operations
up: ## Start all services (API + Ollama)
	@echo "$(BLUE)Starting services...$(RESET)"
	$(DOCKER_COMPOSE) up -d --build
	@echo "$(GREEN)Services started$(RESET)"
	@echo "$(YELLOW)API available at: http://localhost:8000$(RESET)"
	@echo "$(YELLOW)Ollama available at: http://localhost:11434$(RESET)"

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Services stopped$(RESET)"

restart: down up ## Restart all services

logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

logs-api: ## Show logs from API service only
	$(DOCKER_COMPOSE) logs -f $(API_SERVICE)

logs-ollama: ## Show logs from Ollama service only
	$(DOCKER_COMPOSE) logs -f $(OLLAMA_SERVICE)

docker-build: ## Build Docker images without cache
	@echo "$(BLUE)Building Docker images...$(RESET)"
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)Docker images built$(RESET)"

## Testing
test: ## Run tests
	@echo "$(BLUE)Running tests...$(RESET)"
	$(UV) run pytest $(PYTEST_ARGS)

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(UV) run pytest --cov=app --cov-report=html --cov-report=term-missing

## Code Quality
lint: ## Run code linting
	@echo "$(BLUE)Running linter...$(RESET)"
	$(UV) run ruff check .

format: ## Format code
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(UV) run ruff format .

check: lint test ## Run all quality checks (lint + test)
	@echo "$(GREEN)All checks passed$(RESET)"

pre-commit-run: ## Run pre-commit on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	$(UV) run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "$(BLUE)Updating pre-commit hooks...$(RESET)"
	$(UV) run pre-commit autoupdate

## Ollama Model Management
ollama-pull: ## Pull the default model
	@echo "$(BLUE)Pulling model $(DEFAULT_MODEL)...$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_SERVICE) ollama pull $(DEFAULT_MODEL)
	@echo "$(GREEN)Model $(DEFAULT_MODEL) pulled successfully$(RESET)"

ollama-list: ## List available models
	@echo "$(BLUE)Available models:$(RESET)"
	$(DOCKER_COMPOSE) exec $(OLLAMA_SERVICE) ollama list

ollama-models: ollama-list ## Alias for ollama-list

## Cleanup
clean: ## Clean up Docker resources
	@echo "$(BLUE)Cleaning up...$(RESET)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Cleanup completed$(RESET)"

docker-clean: ## Deep clean Docker (removes all unused resources)
	@echo "$(RED)Warning: This will remove ALL unused Docker resources$(RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -a --volumes -f; \
		echo "$(GREEN)Deep clean completed$(RESET)"; \
	else \
		echo "$(YELLOW)Cancelled$(RESET)"; \
	fi

## Development Shortcuts
dev: up ## Start development environment (alias for 'up')

# Check if required tools are installed
check-tools:
	@which $(UV) > /dev/null || (echo "$(RED)Error: uv is not installed$(RESET)" && exit 1)
	@which docker > /dev/null || (echo "$(RED)Error: docker is not installed$(RESET)" && exit 1)
	@which $(DOCKER_COMPOSE) > /dev/null || (echo "$(RED)Error: docker-compose is not installed$(RESET)" && exit 1)

# Run tool checks before most operations
install dev-setup up: | check-tools 