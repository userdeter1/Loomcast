from __future__ import annotations

import json
from typing import Any

import httpx

from loomcast.adapters.downloader.progress import ProgressReporter
from loomcast.common.exceptions import (
    ModelNotFoundError,
    RuntimeExecutionError,
    RuntimeUnavailableError,
)
from loomcast.ports.runtime import RuntimePort


class OllamaRuntime(RuntimePort):
    """Adapter for local Ollama server running on port 11434 (default)."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def list_installed_with_metadata(self) -> list[dict[str, Any]]:
        """List all installed Ollama models with full metadata dictionaries."""
        if not self.is_available():
            raise RuntimeUnavailableError("ollama", self.base_url)
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(
                f"Failed to list Ollama models metadata: {e}"
            ) from e

    def list_installed(self) -> list[str]:
        """List all installed Ollama models."""
        models = self.list_installed_with_metadata()
        return [m["name"] for m in models if "name" in m]

    def get_model_digest(self, model: str) -> str | None:
        """Retrieve the digest string for a specific installed model."""
        models = self.list_installed_with_metadata()
        for m in models:
            name = m.get("name", "")
            if name == model or name == f"{model}:latest":
                return m.get("digest")
        return None

    def is_model_installed(self, model: str) -> bool:
        """Check if a model is installed in Ollama."""
        installed = self.list_installed()
        if model in installed:
            return True
        # Check tag variations, e.g. "llama3" vs "llama3:latest"
        return f"{model}:latest" in installed

    def install(self, model: str, progress: ProgressReporter | None = None) -> None:
        """Pull a model via Ollama API."""
        if not self.is_available():
            raise RuntimeUnavailableError("ollama", self.base_url)

        if progress is not None:
            try:
                with httpx.stream(
                    "POST",
                    f"{self.base_url}/api/pull",
                    json={"name": model, "stream": True},
                    timeout=None,
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line or not line.strip():
                            continue
                        data = json.loads(line)
                        status = data.get("status", "")
                        completed = data.get("completed")
                        total = data.get("total")
                        progress.on_progress(status, completed, total)
            except httpx.HTTPError as e:
                raise RuntimeExecutionError(
                    f"Failed to install Ollama model '{model}': {e}"
                ) from e
            except json.JSONDecodeError as e:
                raise RuntimeExecutionError(
                    f"Invalid JSON response during model pull: {e}"
                ) from e
        else:
            try:
                response = httpx.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model, "stream": False},
                    timeout=None,  # Pulling models can take time
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise RuntimeExecutionError(
                    f"Failed to install Ollama model '{model}': {e}"
                ) from e

    def chat(self, model: str, messages: list[dict[str, Any]]) -> str:
        """Send chat messages to Ollama native API."""
        if not self.is_available():
            raise RuntimeUnavailableError("ollama", self.base_url)
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
            }
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(
                f"Ollama chat execution failed for model '{model}': {e}"
            ) from e

    def remove(self, model: str) -> None:
        """Remove/delete an installed model via Ollama API."""
        if not self.is_available():
            raise RuntimeUnavailableError("ollama", self.base_url)

        if not self.is_model_installed(model):
            raise ModelNotFoundError(model, "ollama")

        try:
            response = httpx.request(
                "DELETE",
                f"{self.base_url}/api/delete",
                json={"name": model},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(
                f"Failed to remove Ollama model '{model}': {e}"
            ) from e

    def update(self, model: str, progress: ProgressReporter | None = None) -> bool:
        """Update an installed Ollama model and return True if digest changed."""
        if not self.is_available():
            raise RuntimeUnavailableError("ollama", self.base_url)

        if not self.is_model_installed(model):
            raise ModelNotFoundError(model, "ollama")

        initial_digest = self.get_model_digest(model)
        self.install(model, progress=progress)
        new_digest = self.get_model_digest(model)

        return initial_digest != new_digest
