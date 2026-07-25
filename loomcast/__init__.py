from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any

from loomcast.adapters.downloader.progress import (
    NullProgressReporter,
    ProgressReporter,
    RichProgressReporter,
)
from loomcast.adapters.runtimes import LlamaCppRuntime
from loomcast.common.config import LoomcastConfig
from loomcast.common.exceptions import (
    CacheError,
    CatalogIntegrityError,
    ConfigurationError,
    LoomcastError,
    ModelNotFoundError,
    RuntimeExecutionError,
    RuntimeUnavailableError,
)
from loomcast.core.manager import LoomcastManager
from loomcast.domain.entities import (
    CatalogEntry,
    ChatMessage,
    ComparisonResult,
    Model,
    RuntimeType,
    VerificationResult,
)

try:
    # Read from installed package metadata so the version is declared in exactly
    # one place (pyproject.toml) and cannot drift.
    __version__ = version("loomcast")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0.dev0"

_default_manager: LoomcastManager | None = None


def get_manager(
    config: LoomcastConfig | None = None,
    refresh: bool = False,
) -> LoomcastManager:
    """Get or create global default LoomcastManager instance."""
    global _default_manager
    if _default_manager is None or refresh:
        _default_manager = LoomcastManager(config=config)
    return _default_manager


def search(query: str) -> list[CatalogEntry]:
    """Search model catalog by query string."""
    return get_manager().search(query)


def recommend(task: str) -> list[CatalogEntry]:
    """Recommend model catalog entries matching a task or tag."""
    return get_manager().recommend(task)


def install_category(
    category: str,
    runtime_type: RuntimeType | str | None = None,
    max_concurrent: int = 3,
    progress: ProgressReporter | None = None,
) -> tuple[list[str], list[str]]:
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
    runtime_type: RuntimeType | str | None = None,
) -> VerificationResult:
    """Verify installed model integrity."""
    return get_manager().verify(model, runtime_type=runtime_type)


def chat(
    model: str,
    messages: list[dict[str, Any]],
    runtime_type: RuntimeType | str | None = None,
) -> str:
    """Send chat messages to a local LLM model."""
    return get_manager().chat(model, messages, runtime_type=runtime_type)


def compare(
    prompt: str,
    runtime_types: list[RuntimeType | str] | None = None,
    model: str | None = None,
    models: dict[RuntimeType, str] | None = None,
    max_concurrent: int = 3,
) -> list[ComparisonResult]:
    """Send one prompt to several runtimes and collect their answers."""
    return get_manager().compare(
        prompt,
        runtime_types=runtime_types,
        model=model,
        models=models,
        max_concurrent=max_concurrent,
    )


def install(
    model: str,
    runtime_type: RuntimeType | str | None = None,
    progress: ProgressReporter | None = None,
) -> None:
    """Install a model into the local runtime."""
    reporter = progress if progress is not None else NullProgressReporter()
    get_manager().install(model, runtime_type=runtime_type, progress=reporter)


def remove(
    model: str,
    runtime_type: RuntimeType | str | None = None,
) -> None:
    """Remove/uninstall an installed model from the local runtime."""
    get_manager().remove(model, runtime_type=runtime_type)


def update(
    model: str,
    runtime_type: RuntimeType | str | None = None,
    progress: ProgressReporter | None = None,
) -> bool:
    """Update an installed model in the local runtime."""
    reporter = progress if progress is not None else NullProgressReporter()
    return get_manager().update(model, runtime_type=runtime_type, progress=reporter)


def list_installed(
    runtime_type: RuntimeType | str | None = None,
) -> list[str]:
    """List installed models in the local runtime."""
    return get_manager().list_installed(runtime_type=runtime_type)


def is_model_installed(
    model: str,
    runtime_type: RuntimeType | str | None = None,
) -> bool:
    """Check if a model is installed in the local runtime."""
    return get_manager().is_model_installed(model, runtime_type=runtime_type)


__all__ = [
    "__version__",
    "CacheError",
    "CatalogEntry",
    "CatalogIntegrityError",
    "ChatMessage",
    "ComparisonResult",
    "ConfigurationError",
    "LlamaCppRuntime",
    "LoomcastConfig",
    "LoomcastError",
    "LoomcastManager",
    "Model",
    "ModelNotFoundError",
    "NullProgressReporter",
    "ProgressReporter",
    "RichProgressReporter",
    "RuntimeExecutionError",
    "RuntimeType",
    "RuntimeUnavailableError",
    "VerificationResult",
    "chat",
    "compare",
    "get_manager",
    "install",
    "install_category",
    "is_model_installed",
    "list_installed",
    "recommend",
    "remove",
    "search",
    "update",
    "verify",
]
