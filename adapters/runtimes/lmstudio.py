from typing import Any, Dict, List
import httpx

from common.exceptions import RuntimeExecutionError, RuntimeUnavailableError
from ports.runtime import RuntimePort


class LMStudioRuntime(RuntimePort):
    """Adapter for local LM Studio server running on port 1234 (OpenAI-compatible)."""

    def __init__(self, base_url: str = "http://localhost:1234", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if LM Studio server is running."""
        try:
            response = httpx.get(f"{self.base_url}/v1/models", timeout=2.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def list_installed(self) -> List[str]:
        """List all loaded/available models in LM Studio."""
        if not self.is_available():
            raise RuntimeUnavailableError("lmstudio", self.base_url)
        try:
            response = httpx.get(f"{self.base_url}/v1/models", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            models = data.get("data", [])
            return [m["id"] for m in models if "id" in m]
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(f"Failed to list LM Studio models: {e}") from e

    def is_model_installed(self, model: str) -> bool:
        """Check if a model is loaded in LM Studio."""
        installed = self.list_installed()
        return model in installed

    def install(self, model: str) -> None:
        """LM Studio model installation directive."""
        if not self.is_available():
            raise RuntimeUnavailableError("lmstudio", self.base_url)
        # LM Studio model pulling is typically handled in the LM Studio application UI.
        # We check if it is loaded, otherwise inform the user.
        if not self.is_model_installed(model):
            raise RuntimeExecutionError(
                f"Model '{model}' is not currently loaded in LM Studio. "
                "Please search and load the model within the LM Studio interface."
            )

    def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
        """Send chat completion request to LM Studio OpenAI-compatible endpoint."""
        if not self.is_available():
            raise RuntimeUnavailableError("lmstudio", self.base_url)
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
            }
            response = httpx.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise RuntimeExecutionError("Empty choices returned from LM Studio chat API.")
            return choices[0].get("message", {}).get("content", "")
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(f"LM Studio chat execution failed for model '{model}': {e}") from e
