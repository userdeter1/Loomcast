from typing import Any, Dict, List, Optional, Union

from adapters.runtimes.lmstudio import LMStudioRuntime
from adapters.runtimes.ollama import OllamaRuntime
from common.config import LoomcastConfig
from common.exceptions import LoomcastError, RuntimeUnavailableError
from domain.entities import RuntimeType
from ports.runtime import RuntimePort


class LoomcastManager:
    """Orchestrator for managing local LLM runtimes and model operations."""

    def __init__(self, config: Optional[LoomcastConfig] = None):
        self.config = config or LoomcastConfig.load()
        self.runtimes: Dict[RuntimeType, RuntimePort] = {
            RuntimeType.OLLAMA: OllamaRuntime(base_url=self.config.ollama_url),
            RuntimeType.LMSTUDIO: LMStudioRuntime(base_url=self.config.lmstudio_url),
        }

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
