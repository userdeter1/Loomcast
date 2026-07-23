from __future__ import annotations

from typing import Any

import httpx

from loomcast.adapters.downloader.progress import ProgressReporter
from loomcast.adapters.runtimes._openai_compat import send_openai_compat_chat
from loomcast.common.exceptions import RuntimeExecutionError, RuntimeUnavailableError
from loomcast.ports.runtime import RuntimePort


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

    def list_installed(self) -> list[str]:
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

    def install(self, model: str, progress: ProgressReporter | None = None) -> None:
        """LM Studio model installation directive.

        Note:
            LM Studio does not support remote model downloading via API.
            The `progress` parameter is accepted to respect the RuntimePort interface,
            but is ignored here.
        """
        if not self.is_available():
            raise RuntimeUnavailableError("lmstudio", self.base_url)
        # LM Studio model pulling is typically handled in the LM Studio application UI.
        # We check if it is loaded, otherwise inform the user.
        if not self.is_model_installed(model):
            raise RuntimeExecutionError(
                f"Model '{model}' is not currently loaded in LM Studio. "
                "Please search and load the model within the LM Studio interface."
            )

    def chat(self, model: str, messages: list[dict[str, Any]]) -> str:
        """Send chat completion request to LM Studio OpenAI-compatible endpoint."""
        if not self.is_available():
            raise RuntimeUnavailableError("lmstudio", self.base_url)
        return send_openai_compat_chat(
            base_url=self.base_url,
            model=model,
            messages=messages,
            timeout=self.timeout,
            runtime_name="LM Studio",
        )

    def remove(self, model: str) -> None:
        """LM Studio model removal directive."""
        raise RuntimeExecutionError(
            f"LM Studio does not support model deletion via API. "
            f"Please remove '{model}' manually within the LM Studio interface."
        )

    def update(self, model: str, progress: ProgressReporter | None = None) -> bool:
        """LM Studio model update directive."""
        if not self.is_available():
            raise RuntimeUnavailableError("lmstudio", self.base_url)
        raise RuntimeExecutionError(
            "LM Studio does not support model updating via API. "
            "Please search and load the model within the LM Studio interface."
        )
