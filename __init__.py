"""Loomcast: Multi-runtime Local LLM Manager SDK & CLI."""

from adapters.runtimes.lmstudio import LMStudioRuntime
from adapters.runtimes.ollama import OllamaRuntime
from common.config import LoomcastConfig
from common.exceptions import (
    ConfigurationError,
    LoomcastError,
    ModelNotFoundError,
    RuntimeExecutionError,
    RuntimeUnavailableError,
)
from core.manager import LoomcastManager
from domain.entities import CatalogEntry, ChatMessage, Model, RuntimeType
from ports.runtime import RuntimePort

__version__ = "0.1.0"


# Helper convenience functions for quick SDK access
def get_manager() -> LoomcastManager:
    """Instantiate a LoomcastManager with default configuration."""
    return LoomcastManager()


def list_runtimes():
    """List operational status of available local runtimes."""
    return get_manager().list_available_runtimes()


def chat(model: str, messages: list, runtime: str = None) -> str:
    """Send chat prompt to a local model via LoomcastManager."""
    return get_manager().chat(model, messages, runtime_type=runtime)


def install(model: str, runtime: str = None) -> None:
    """Install/pull a model into the local runtime."""
    get_manager().install(model, runtime_type=runtime)


__all__ = [
    "LoomcastManager",
    "RuntimeType",
    "Model",
    "CatalogEntry",
    "ChatMessage",
    "RuntimePort",
    "OllamaRuntime",
    "LMStudioRuntime",
    "LoomcastConfig",
    "LoomcastError",
    "RuntimeUnavailableError",
    "ModelNotFoundError",
    "ConfigurationError",
    "RuntimeExecutionError",
    "get_manager",
    "list_runtimes",
    "chat",
    "install",
]
