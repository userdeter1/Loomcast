from typing import Any, Dict, List
import httpx

from common.exceptions import RuntimeExecutionError, RuntimeUnavailableError
from ports.runtime import RuntimePort


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

    def list_installed(self) -> List[str]:
        """List all installed Ollama models."""
        if not self.is_available():
            raise RuntimeUnavailableError("ollama", self.base_url)
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            return [m["name"] for m in models if "name" in m]
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(f"Failed to list Ollama models: {e}") from e

    def is_model_installed(self, model: str) -> bool:
        """Check if a model is installed in Ollama."""
        installed = self.list_installed()
        if model in installed:
            return True
        # Check tag variations, e.g. "llama3" vs "llama3:latest"
        if f"{model}:latest" in installed:
            return True
        return False

    def install(self, model: str) -> None:
        """Pull a model via Ollama API."""
        if not self.is_available():
            raise RuntimeUnavailableError("ollama", self.base_url)
        try:
            response = httpx.post(
                f"{self.base_url}/api/pull",
                json={"name": model, "stream": False},
                timeout=None,  # Pulling models can take time
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(f"Failed to install Ollama model '{model}': {e}") from e

    def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
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
            raise RuntimeExecutionError(f"Ollama chat execution failed for model '{model}': {e}") from e
