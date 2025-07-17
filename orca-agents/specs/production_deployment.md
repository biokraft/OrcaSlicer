# Production Deployment Specification

## 1. Purpose

This document outlines the strategy and configuration for deploying the Orca Agents backend to a production environment. It covers infrastructure, security, monitoring, and scaling to ensure a robust and reliable service.

## 2. Guiding Principles

- **Immutability**: Docker images are considered immutable artifacts. No changes are made to running containers.
- **Infrastructure as Code**: All infrastructure components (Docker Compose files, NGINX configs) are version-controlled in the repository.
- **Security by Default**: The system is designed with security in mind, including network policies and resource limits.

## 3. Production `docker-compose.prod.yml`

A separate `docker-compose.prod.yml` file will be used for production deployments.

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  ollama-chat:
    container_name: "prod-ollama-chat"
    image: ollama/ollama:${OLLAMA_VERSION:-latest}
    volumes:
      - ollama_chat_data:/root/.ollama
    networks:
      - app-network
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: ${CHAT_MEMORY_LIMIT:-4G}
        reservations:
          memory: ${CHAT_MEMORY_RESERVATION:-2G}

  ollama-reasoning:
    container_name: "prod-ollama-reasoning"
    image: ollama/ollama:${OLLAMA_VERSION:-latest}
    volumes:
      - ollama_reasoning_data:/root/.ollama
    networks:
      - app-network
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: ${REASONING_MEMORY_LIMIT:-16G}
        reservations:
          memory: ${REASONING_MEMORY_RESERVATION:-8G}

  api:
    image: my-registry/orca-agents:${IMAGE_TAG:-latest} # Use a specific image tag
    depends_on:
      ollama-chat:
        condition: service_healthy
      ollama-reasoning:
        condition: service_healthy
    environment:
      - CHAT_OLLAMA_URL=http://ollama-chat:11434
      - REASONING_OLLAMA_URL=http://ollama-reasoning:11434
      # ... other production secrets and config
    restart: unless-stopped
    # ... other production settings (ports, etc.)

volumes:
  ollama_chat_data:
  ollama_reasoning_data:

networks:
  app-network:
    driver: bridge
```

## 4. Security

- **Reverse Proxy**: An NGINX reverse proxy should be placed in front of the `api` service to handle TLS termination, rate limiting, and security headers.
- **Environment Variables**: Production secrets (API keys, etc.) must be injected securely into the container environment using a secrets management tool (e.g., Doppler, AWS Secrets Manager) and not committed to the repository.
- **Resource Limiting**: The `docker-compose.prod.yml` file defines strict memory and CPU limits for both `ollama` services to prevent resource exhaustion.

## 5. Monitoring and Observability

- **Structured Logging**: All services will use a `json-file` logging driver, forwarding logs to a central aggregation service (e.g., Datadog, ELK stack).
- **Metrics**: The architecture is designed to be scraped by a Prometheus instance. Key metrics to monitor include:
    - Health and response times for both Ollama services.
    - API endpoint latency and error rates.
    - System-level metrics (CPU, memory) for all containers.
- **Alerting**: Alerts will be configured in Prometheus/Alertmanager for critical conditions, such as:
    - Either Ollama service being down for more than 2 minutes.
    - API error rate exceeding 5%.
    - High memory or CPU usage.

## 6. Maintenance

- **Model Updates**: Updating LLM models will be achieved by updating the `OLLAMA_MODELS` variable in the environment, and re-running the `ollama-init` service or redeploying the stack.
- **Zero-Downtime Deployments**: For critical applications, a blue-green deployment strategy should be implemented at the reverse proxy level to ensure seamless updates. 