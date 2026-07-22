from typing import Any, Dict, List, Optional, Tuple, Union

from loomcast.adapters.downloader.progress import (
    NullProgressReporter,
    ProgressReporter,
    RichProgressReporter,
)
from loomcast.common.config import LoomcastConfig
from loomcast.common.exceptions import (
    CacheError,
    ConfigurationError,
    LoomcastError,
    ModelNotFoundError,
    RuntimeExecutionError,
    RuntimeUnavailableError,
)
from loomcast.adapters.runtimes import LlamaCppRuntime
from loomcast.core.manager import LoomcastManager
from loomcast.domain.entities import CatalogEntry, ChatMessage, Model, RuntimeType, VerificationResult

_default_manager: Optional[LoomcastManager] = None


def get_manager(
    config: Optional[LoomcastConfig] = None,
    refresh: bool = False,
) -> LoomcastManager:
    """Get or create global default LoomcastManager instance."""
    global _default_manager
    if _default_manager is None or refresh:
        _default_manager = LoomcastManager(config=config)
    return _default_manager


def search(query: str) -> List[CatalogEntry]:
    """Search model catalog by query string."""
    return get_manager().search(query)


def recommend(task: str) -> List[CatalogEntry]:
    """Recommend model catalog entries matching a task or tag."""
    return get_manager().recommend(task)


def install_category(
    category: str,
    runtime_type: Optional[Union[RuntimeType, str]] = None,
    max_concurrent: int = 3,
    progress: Optional[ProgressReporter] = None,
) -> Tuple[List[str], List[str]]:
    """Batch install all models in a category."""
    reporter = progress if progress is not None else NullProgressReporter()
    return get_manager().install_category(
        category,
        runtime_type=runtime_type,
        max_concurrent=max_concurrent,
        progress=reporter,
    )


def verify(
    model: str,
    runtime_type: Optional[Union[RuntimeType, str]] = None,
) -> VerificationResult:
    """Verify installed model integrity."""
    return get_manager().verify(model, runtime_type=runtime_type)


def chat(
    model: str,
    messages: List[Dict[str, Any]],
    runtime_type: Optional[Union[RuntimeType, str]] = None,
) -> str:
    """Send chat messages to a local LLM model."""
    return get_manager().chat(model, messages, runtime_type=runtime_type)


def install(
    model: str,
    runtime_type: Optional[Union[RuntimeType, str]] = None,
    progress: Optional[ProgressReporter] = None,
) -> None:
    """Install a model into the local runtime."""
    reporter = progress if progress is not None else NullProgressReporter()
    get_manager().install(model, runtime_type=runtime_type, progress=reporter)


def list_installed(
    runtime_type: Optional[Union[RuntimeType, str]] = None,
) -> List[str]:
    """List installed models in the local runtime."""
    return get_manager().list_installed(runtime_type=runtime_type)


def is_model_installed(
    model: str,
    runtime_type: Optional[Union[RuntimeType, str]] = None,
) -> bool:
    """Check if a model is installed in the local runtime."""
    return get_manager().is_model_installed(model, runtime_type=runtime_type)


__all__ = [
    "LoomcastManager",
    "get_manager",
    "search",
    "recommend",
    "install_category",
    "verify",
    "chat",
    "install",
    "list_installed",
    "is_model_installed",
    "ProgressReporter",
    "RichProgressReporter",
    "NullProgressReporter",
    "LlamaCppRuntime",
    "LoomcastConfig",
    "LoomcastError",
    "RuntimeUnavailableError",
    "ModelNotFoundError",
    "ConfigurationError",
    "RuntimeExecutionError",
    "CacheError",
    "RuntimeType",
    "Model",
    "CatalogEntry",
    "ChatMessage",
    "VerificationResult",
]
