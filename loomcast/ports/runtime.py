from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RuntimePort(Protocol):
    """Abstract port definition for local LLM runtime interactions."""

    def is_available(self) -> bool:
        """Check if the local runtime daemon/server is running and reachable."""
        ...

    def is_model_installed(self, model: str) -> bool:
        """Check if a specific model is installed/loaded in this runtime."""
        ...

    def install(self, model: str, progress: Any | None = None) -> None:
        """Install or pull a model into the local runtime."""
        ...

    def chat(self, model: str, messages: list[dict[str, Any]]) -> str:
        """Send a list of messages to a model and return the generated text response."""
        ...

    def list_installed(self) -> list[str]:
        """List all installed/available model names in this runtime."""
        ...

    def remove(self, model: str) -> None:
        """Remove or delete an installed model from the local runtime."""
        ...

    def update(self, model: str, progress: Any | None = None) -> bool:
        """Update an installed model in the local runtime and return True if digest changed."""
        ...
