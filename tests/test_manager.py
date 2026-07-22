from loomcast.common.config import LoomcastConfig
from loomcast.common.exceptions import RuntimeExecutionError
from loomcast.core.manager import LoomcastManager
from loomcast.domain.entities import CatalogEntry, RuntimeType
from loomcast.ports.catalog import CatalogPort
from loomcast.ports.runtime import RuntimePort


class DummyCatalogAdapter(CatalogPort):
    def __init__(self):
        self.entries = [
            CatalogEntry(
                name="codellama",
                description="Code generation model",
                publisher="meta",
                tags=["code", "python"],
                default_runtime=RuntimeType.OLLAMA,
            ),
            CatalogEntry(
                name="deepseek-coder",
                description="DeepSeek code model",
                publisher="deepseek",
                tags=["code", "math"],
                default_runtime=RuntimeType.OLLAMA,
            ),
            CatalogEntry(
                name="llama3",
                description="General purpose model",
                publisher="meta",
                tags=["general", "chat"],
                default_runtime=RuntimeType.OLLAMA,
            ),
        ]

    def search(self, query: str):
        q = query.lower()
        return [
            e for e in self.entries
            if q in e.name.lower() or q in (e.description or "").lower() or any(q in t.lower() for t in e.tags)
        ]

    def get_entry(self, name: str):
        for e in self.entries:
            if e.name.lower() == name.lower():
                return e
        return None


class PartialFailureRuntimeAdapter(RuntimePort):
    def __init__(self):
        self.installed = []

    def is_available(self) -> bool:
        return True

    def is_model_installed(self, model: str) -> bool:
        return model in self.installed

    def install(self, model: str) -> None:
        if "deepseek" in model:
            raise RuntimeExecutionError(f"Simulated failure for {model}")
        self.installed.append(model)

    def chat(self, model: str, messages: list) -> str:
        return "ok"

    def list_installed(self) -> list:
        return list(self.installed)


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


def test_manager_search_and_recommend():
    catalog = DummyCatalogAdapter()
    manager = LoomcastManager(catalog=catalog)

    search_results = manager.search("code")
    assert len(search_results) == 2

    recommend_results = manager.recommend("code")
    assert len(recommend_results) == 2
    names = [e.name for e in recommend_results]
    assert "codellama" in names
    assert "deepseek-coder" in names


def test_manager_install_category_partial_failure():
    catalog = DummyCatalogAdapter()
    adapter = PartialFailureRuntimeAdapter()
    manager = LoomcastManager(catalog=catalog)
    manager.runtimes[RuntimeType.OLLAMA] = adapter

    installed, failed = manager.install_category("code", runtime_type=RuntimeType.OLLAMA)

    assert "codellama" in installed
    assert "deepseek-coder" in failed
    assert len(installed) == 1
    assert len(failed) == 1
