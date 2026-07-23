from typing import Any, Dict, List
from loomcast.ports.cache import CachePort
from loomcast.ports.catalog import CatalogPort
from loomcast.ports.runtime import RuntimePort


class DummyRuntimeAdapter:
    """Pure mock implementation of RuntimePort without network calls."""

    def __init__(self):
        self._installed = ["llama3:latest", "mistral:latest"]
        self._available = True

    def is_available(self) -> bool:
        return self._available

    def is_model_installed(self, model: str) -> bool:
        return model in self._installed

    def install(self, model: str) -> None:
        if model not in self._installed:
            self._installed.append(model)

    def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
        return f"Response to {messages[-1]['content']} from {model}"

    def list_installed(self) -> List[str]:
        return list(self._installed)

    def remove(self, model: str) -> None:
        if model in self._installed:
            self._installed.remove(model)

    def update(self, model: str, progress: Any = None) -> bool:
        return False


def test_runtime_port_protocol_compliance():
    adapter = DummyRuntimeAdapter()
    assert isinstance(adapter, RuntimePort)
    assert adapter.is_available() is True
    assert adapter.is_model_installed("llama3:latest") is True
    assert adapter.is_model_installed("nonexistent") is False

    adapter.install("phi3:latest")
    assert adapter.is_model_installed("phi3:latest") is True
    adapter.remove("phi3:latest")
    assert adapter.is_model_installed("phi3:latest") is False

    response = adapter.chat("llama3:latest", [{"role": "user", "content": "Hi"}])
    assert response == "Response to Hi from llama3:latest"
    assert "phi3:latest" not in adapter.list_installed()


def test_protocol_runtime_check():
    class IncompleteAdapter:
        pass

    assert not isinstance(IncompleteAdapter(), RuntimePort)
    assert not isinstance(IncompleteAdapter(), CatalogPort)
    assert not isinstance(IncompleteAdapter(), CachePort)
