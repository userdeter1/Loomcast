from typing import Any, Dict, List, Optional, Tuple, Union

from loomcast.adapters.cache.store import FileSystemCache
from loomcast.adapters.catalog.dynamic import DynamicCatalog
from loomcast.adapters.catalog.static import StaticCatalog
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
        config: Optional[LoomcastConfig] = None,
        catalog: Optional[CatalogPort] = None,
    ):
        self.config = config or LoomcastConfig.load()
        self.runtimes: Dict[RuntimeType, RuntimePort] = {
            RuntimeType.OLLAMA: OllamaRuntime(base_url=self.config.ollama_url),
            RuntimeType.LMSTUDIO: LMStudioRuntime(base_url=self.config.lmstudio_url),
        }
        self.catalog: CatalogPort = catalog if catalog is not None else DynamicCatalog(
            cache=FileSystemCache(),
            fallback_catalog=StaticCatalog(),
        )

    def _resolve_runtime_type(self, runtime_type: Optional[Union[RuntimeType, str]] = None) -> RuntimeType:
        if runtime_type is None:
            return self.config.default_backend
        if isinstance(runtime_type, str):
            try:
                return RuntimeType(runtime_type.lower())
            except ValueError:
                raise LoomcastError(f"Unsupported runtime type: '{runtime_type}'")
        return runtime_type

    def get_runtime(self, runtime_type: Optional[Union[RuntimeType, str]] = None) -> RuntimePort:
        """Get the specified or default runtime adapter instance."""
        target_type = self._resolve_runtime_type(runtime_type)
        return self.runtimes[target_type]

    def list_available_runtimes(self) -> Dict[RuntimeType, bool]:
        """Check availability status across all configured runtimes."""
        return {
            rtype: adapter.is_available()
            for rtype, adapter in self.runtimes.items()
        }

    def list_installed(self, runtime_type: Optional[Union[RuntimeType, str]] = None) -> List[str]:
        """List installed model names for a specific runtime (or default backend)."""
        adapter = self.get_runtime(runtime_type)
        return adapter.list_installed()

    def is_model_installed(self, model: str, runtime_type: Optional[Union[RuntimeType, str]] = None) -> bool:
        """Check if a model is installed in the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        return adapter.is_model_installed(model)

    def install(self, model: str, runtime_type: Optional[Union[RuntimeType, str]] = None) -> None:
        """Install a model into the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        adapter.install(model)

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        runtime_type: Optional[Union[RuntimeType, str]] = None,
    ) -> str:
        """Send chat messages to a model in the specified or default runtime."""
        adapter = self.get_runtime(runtime_type)
        return adapter.chat(model, messages)

    def verify(
        self,
        model: str,
        runtime_type: Optional[Union[RuntimeType, str]] = None,
    ) -> VerificationResult:
        """Verify installed model integrity using ModelVerifier."""
        target_type = self._resolve_runtime_type(runtime_type)
        verifier = ModelVerifier(self.runtimes)
        return verifier.verify(model, target_type)

    def search(self, query: str) -> List[CatalogEntry]:
        """Search the model catalog by query string."""
        return self.catalog.search(query)

    def recommend(self, task: str) -> List[CatalogEntry]:
        """Recommend catalog models matching a specific task or tag."""
        all_matches = self.catalog.search(task)
        task_lower = task.lower()
        tag_matches = [
            entry for entry in all_matches
            if any(task_lower in tag.lower() for tag in entry.tags)
        ]
        return tag_matches if tag_matches else all_matches

    def install_category(
        self,
        category: str,
        runtime_type: Optional[Union[RuntimeType, str]] = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Batch install all models tagged under a given category.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing (installed_models, failed_models).
            Does not stop on individual installation failures, but logs errors.
        """
        entries = self.recommend(category)
        installed: List[str] = []
        failed: List[str] = []

        for entry in entries:
            try:
                self.install(entry.name, runtime_type=runtime_type)
                installed.append(entry.name)
            except Exception as e:
                logger.warning(f"Failed to install model '{entry.name}' in category '{category}': {e}")
                failed.append(entry.name)

        return installed, failed
