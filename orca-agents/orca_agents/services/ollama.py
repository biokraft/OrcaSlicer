"""Ollama service for AI model interactions."""

import json
from collections.abc import AsyncIterator

import httpx
from fastapi import HTTPException

from ..config import get_settings


class OllamaService:
    """Service for interacting with Ollama API."""

    def __init__(self) -> None:
        """Initialize the Ollama service."""
        self.settings = get_settings()
        self.base_url = self.settings.ollama_url
        self.timeout = self.settings.ollama_timeout

    async def health_check(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available models in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to list models: {e.response.text}",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error connecting to Ollama: {str(e)}",
            ) from e

    async def generate_response(
        self,
        message: str,
        model: str | None = None,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """Generate a response using Ollama."""
        model_name = model or self.settings.default_model

        # Check if model is available
        available_models = await self.list_models()
        if model_name not in available_models:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model_name}' not available. Available models: {available_models}",
            )

        payload = {
            "model": model_name,
            "prompt": message,
            "stream": stream,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if stream:
                    return self._stream_response(client, payload)
                else:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data.get("response", "")

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Ollama API error: {e.response.text}",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response: {str(e)}",
            ) from e

    async def _stream_response(
        self,
        client: httpx.AsyncClient,
        payload: dict,
    ) -> AsyncIterator[str]:
        """Stream response from Ollama."""
        async with client.stream(
            "POST",
            f"{self.base_url}/api/generate",
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue


# Global instance
ollama_service = OllamaService()
