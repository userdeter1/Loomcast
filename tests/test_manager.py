from common.config import LoomcastConfig
from core.manager import LoomcastManager
from domain.entities import RuntimeType


def test_manager_initialization():
    config = LoomcastConfig(default_backend=RuntimeType.OLLAMA)
    manager = LoomcastManager(config=config)
    assert manager.config.default_backend == RuntimeType.OLLAMA
    assert RuntimeType.OLLAMA in manager.runtimes
    assert RuntimeType.LMSTUDIO in manager.runtimes


def test_manager_resolve_runtime():
    manager = LoomcastManager()
    assert manager._resolve_runtime_type(None) == RuntimeType.OLLAMA
    assert manager._resolve_runtime_type("ollama") == RuntimeType.OLLAMA
    assert manager._resolve_runtime_type("lmstudio") == RuntimeType.LMSTUDIO
    assert manager._resolve_runtime_type(RuntimeType.LMSTUDIO) == RuntimeType.LMSTUDIO
