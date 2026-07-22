from typing import Any, Dict, List, Optional
import httpx

from loomcast.adapters.downloader.progress import ProgressReporter
from loomcast.adapters.runtimes._openai_compat import send_openai_compat_chat
from loomcast.common.exceptions import RuntimeExecutionError, RuntimeUnavailableError
from loomcast.ports.runtime import RuntimePort


class LlamaCppRuntime(RuntimePort):
    """Adapter for local llama.cpp server (llama-server) running on port 8080 (default)."""

    def __init__(self, base_url: str = "http://localhost:8080", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if llama-server is running via GET /health."""
        try:
            response = httpx.get(f"{self.base_url}/health", timeout=2.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def list_installed(self) -> List[str]:
        """List model currently loaded in llama-server.

        Note:
            llama-server typically serves a single model specified at server launch.
            This queries GET /v1/models to retrieve the active model identifier.
        """
        if not self.is_available():
            raise RuntimeUnavailableError("llamacpp", self.base_url)
        try:
            response = httpx.get(f"{self.base_url}/v1/models", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            models = data.get("data", [])
            return [m["id"] for m in models if "id" in m]
        except httpx.HTTPError as e:
            raise RuntimeExecutionError(f"Failed to list llama.cpp models: {e}") from e

    def is_model_installed(self, model: str) -> bool:
        """Check if a model is currently loaded in llama-server."""
        installed = self.list_installed()
        return model in installed

    def install(self, model: str, progress: Optional[ProgressReporter] = None) -> None:
        """llama.cpp model installation directive.

        Note:
            llama.cpp does not support remote model downloading via HTTP API.
            Models must be loaded by launching llama-server with command-line flags.
        """
        if not self.is_available():
            raise RuntimeUnavailableError("llamacpp", self.base_url)
        if not self.is_model_installed(model):
            raise RuntimeExecutionError(
                f"Model '{model}' is not currently loaded in llama.cpp. "
                "Please launch llama-server with your desired model specified via command-line flags."
            )

    def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
        """Send chat completion request to llama-server OpenAI-compatible endpoint."""
        if not self.is_available():
            raise RuntimeUnavailableError("llamacpp", self.base_url)
        return send_openai_compat_chat(
            base_url=self.base_url,
            model=model,
            messages=messages,
            timeout=self.timeout,
            runtime_name="llama.cpp",
        )
