from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from loomcast.adapters.cache.store import FileSystemCache
from loomcast.adapters.catalog.dynamic import DynamicCatalog
from loomcast.adapters.catalog.static import StaticCatalog
from loomcast.adapters.downloader.progress import ProgressReporter
from loomcast.adapters.runtimes.llamacpp import LlamaCppRuntime
from loomcast.adapters.runtimes.lmstudio import LMStudioRuntime
from loomcast.adapters.runtimes.ollama import OllamaRuntime
from loomcast.common.config import LoomcastConfig
from loomcast.common.exceptions import LoomcastError
from loomcast.common.logging import logger
from loomcast.core.verifier import ModelVerifier
from loomcast.domain.entities import CatalogEntry, RuntimeType, VerificationResult
from loomcast.ports.catalog import CatalogPort
from loomcast.ports.runtime import RuntimePort


class LoomcastManager:
    """Orchestrator for managing local LLM runtimes, model catalog, and operations."""

    def __init__(
        self,
        config: LoomcastConfig | None = None,
        catalog: CatalogPort | None = None,
    ):
        self.config = config or LoomcastConfig.load()
        self.runtimes: dict[RuntimeType, RuntimePort] = {
            RuntimeType.OLLAMA: OllamaRuntime(base_url=self.config.ollama_url),
            RuntimeType.LMSTUDIO: LMStudioRuntime(base_url=self.config.lmstudio_url),
            RuntimeType.LLAMACPP: LlamaCppRuntime(base_url=self.config.llamacpp_url),
        }
        self.catalog: CatalogPort = (
            catalog
            if catalog is not None
            else DynamicCatalog(
                cache=FileSystemCache(),
                fallback_catalog=StaticCatalog(),
            )
        )

    def _resolve_runtime_type(
        self, runtime_type: RuntimeType | str | None = None
    ) -> RuntimeType:
        if runtime_type is None:
            return self.config.default_backend
        if isinstance(runtime_type, str):
            try:
                return RuntimeType(runtime_type.lower())
            except ValueError as e:
                raise LoomcastError(
                    f"Unsupported runtime type: '{runtime_type}'"
                ) from e
        return runtime_type

    def get_runtime(self, runtime_type: RuntimeType | str | None = None) -> RuntimePort:
        """Get the specified or default runtime adapter instance."""
        target_type = self._resolve_runtime_type(runtime_type)
        return self.runtimes[target_type]

    def list_available_runtimes(self) -> dict[RuntimeType, bool]:
        """Check availability status across all configured runtimes."""
        return {
            rtype: adapter.is_available() for rtype, adapter in self.runtimes.items()
        }

    def list_installed(
        self, runtime_type: RuntimeType | str | None = None
    ) -> list[str]:
        """List installed model names for a specific runtime (or default backend)."""
        adapter = self.get_runtime(runtime_type)
        return adapter.list_installed()

    def is_model_installed(
        self, model: str, runtime_type: RuntimeType | str | None = None
    ) -> bool:
        """Check if a model is installed in the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        return adapter.is_model_installed(model)

    def install(
        self,
        model: str,
        runtime_type: RuntimeType | str | None = None,
        progress: ProgressReporter | None = None,
    ) -> None:
        """Install a model into the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        if progress is not None:
            adapter.install(model, progress=progress)
        else:
            adapter.install(model)

    def remove(
        self,
        model: str,
        runtime_type: RuntimeType | str | None = None,
    ) -> None:
        """Remove/uninstall a model from the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        adapter.remove(model)

    def update(
        self,
        model: str,
        runtime_type: RuntimeType | str | None = None,
        progress: ProgressReporter | None = None,
    ) -> bool:
        """Update an installed model in the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        if progress is not None:
            return adapter.update(model, progress=progress)
        return adapter.update(model)

    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        runtime_type: RuntimeType | str | None = None,
    ) -> str:
        """Send chat messages to a model in the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        return adapter.chat(model, messages)

    def verify(
        self,
        model: str,
        runtime_type: RuntimeType | str | None = None,
    ) -> VerificationResult:
        """Verify installed model integrity using ModelVerifier."""
        target_type = self._resolve_runtime_type(runtime_type)
        verifier = ModelVerifier(self.runtimes)
        return verifier.verify(model, target_type)

    def search(self, query: str) -> list[CatalogEntry]:
        """Search the model catalog by query string."""
        return self.catalog.search(query)

    def recommend(self, task: str) -> list[CatalogEntry]:
        """Recommend catalog models matching a specific task or tag."""
        all_matches = self.catalog.search(task)
        task_lower = task.lower()
        tag_matches = [
            entry
            for entry in all_matches
            if any(task_lower in tag.lower() for tag in entry.tags)
        ]
        return tag_matches if tag_matches else all_matches

    def install_category(
        self,
        category: str,
        runtime_type: RuntimeType | str | None = None,
        max_concurrent: int = 3,
        progress: ProgressReporter | None = None,
    ) -> tuple[list[str], list[str]]:
        """
        Batch install all models tagged under a given category.

        Args:
            category: Category tag to query recommendations.
            runtime_type: Target runtime backend override.
            max_concurrent: Maximum concurrent installations (defaults to 3).
            progress: Optional progress reporter for download feedback.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing (installed_models, failed_models).
            Does not stop on individual installation failures, but tracks futures individually.
        """
        entries = self.recommend(category)
        if not entries:
            return [], []

        installed: list[str] = []
        failed: list[str] = []

        def _install_single(entry: CatalogEntry) -> str:
            item_progress = (
                progress.create_sub_reporter(entry.name)
                if progress is not None
                else None
            )
            self.install(entry.name, runtime_type=runtime_type, progress=item_progress)
            return entry.name

        effective_workers = max(1, max_concurrent)
        with ThreadPoolExecutor(max_workers=effective_workers) as executor:
            future_to_entry = {
                executor.submit(_install_single, entry): entry for entry in entries
            }

            for future in as_completed(future_to_entry):
                entry = future_to_entry[future]
                try:
                    name = future.result()
                    installed.append(name)
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        f"Failed to install model '{entry.name}' in category '{category}': {e}"
                    )
                    failed.append(entry.name)

        return installed, failed
