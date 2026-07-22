import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class RuntimePort(Protocol):
    """Abstract port definition for local LLM runtime interactions."""

    def is_available(self) -> bool:
        """Check if the local runtime daemon/server is running and reachable."""
        ...

    def is_model_installed(self, model: str) -> bool:
        """Check if a specific model is installed/loaded in this runtime."""
        ...

    def install(self, model: str, progress: Optional[Any] = None) -> None:
        """Install or pull a model into the local runtime."""
        ...

    def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
        """Send a list of messages to a model and return the generated text response."""
        ...

    def list_installed(self) -> List[str]:
        """List all installed/available model names in this runtime."""
        ...
