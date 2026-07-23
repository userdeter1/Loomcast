import threading
import time
from typing import Any, Optional

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
            CatalogEntry(
                name="starcoder",
                description="StarCoder code model",
                publisher="bigcode",
                tags=["code"],
                default_runtime=RuntimeType.OLLAMA,
            ),
            CatalogEntry(
                name="wizardcoder",
                description="WizardCoder code model",
                publisher="wizard",
                tags=["code"],
                default_runtime=RuntimeType.OLLAMA,
            ),
        ]

    def search(self, query: str):
        q = query.lower()
        return [
            e
            for e in self.entries
            if q in e.name.lower()
            or q in (e.description or "").lower()
            or any(q in t.lower() for t in e.tags)
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

    def install(self, model: str, progress: Optional[Any] = None) -> None:
        if "deepseek" in model:
            raise RuntimeExecutionError(f"Simulated failure for {model}")
        self.installed.append(model)

    def chat(self, model: str, messages: list) -> str:
        return "ok"

    def list_installed(self) -> list:
        return list(self.installed)


class ConcurrencyTrackingRuntimeAdapter(RuntimePort):
    def __init__(self):
        self.lock = threading.Lock()
        self.active_count = 0
        self.max_active_observed = 0
        self.installed = []

    def is_available(self) -> bool:
        return True

    def is_model_installed(self, model: str) -> bool:
        return model in self.installed

    def install(self, model: str, progress: Optional[Any] = None) -> None:
        with self.lock:
            self.active_count += 1
            if self.active_count > self.max_active_observed:
                self.max_active_observed = self.active_count

        time.sleep(0.05)

        with self.lock:
            self.active_count -= 1
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
    assert len(search_results) == 4

    recommend_results = manager.recommend("code")
    assert len(recommend_results) == 4
    names = [e.name for e in recommend_results]
    assert "codellama" in names
    assert "deepseek-coder" in names


def test_manager_install_category_partial_failure():
    catalog = DummyCatalogAdapter()
    adapter = PartialFailureRuntimeAdapter()
    manager = LoomcastManager(catalog=catalog)
    manager.runtimes[RuntimeType.OLLAMA] = adapter

    installed, failed = manager.install_category(
        "code", runtime_type=RuntimeType.OLLAMA, max_concurrent=1
    )

    assert "codellama" in installed
    assert "deepseek-coder" in failed
    assert len(installed) == 3
    assert len(failed) == 1


def test_install_category_parallel_matches_sequential_result():
    catalog = DummyCatalogAdapter()

    # Run sequential (max_concurrent=1)
    seq_adapter = PartialFailureRuntimeAdapter()
    seq_manager = LoomcastManager(catalog=catalog)
    seq_manager.runtimes[RuntimeType.OLLAMA] = seq_adapter
    seq_installed, seq_failed = seq_manager.install_category(
        "code", runtime_type=RuntimeType.OLLAMA, max_concurrent=1
    )

    # Run parallel (max_concurrent=3)
    par_adapter = PartialFailureRuntimeAdapter()
    par_manager = LoomcastManager(catalog=catalog)
    par_manager.runtimes[RuntimeType.OLLAMA] = par_adapter
    par_installed, par_failed = par_manager.install_category(
        "code", runtime_type=RuntimeType.OLLAMA, max_concurrent=3
    )

    assert set(seq_installed) == set(par_installed)
    assert set(seq_failed) == set(par_failed)


def test_install_category_parallel_partial_failure():
    catalog = DummyCatalogAdapter()
    par_adapter = PartialFailureRuntimeAdapter()
    par_manager = LoomcastManager(catalog=catalog)
    par_manager.runtimes[RuntimeType.OLLAMA] = par_adapter

    installed, failed = par_manager.install_category(
        "code", runtime_type=RuntimeType.OLLAMA, max_concurrent=3
    )

    assert "deepseek-coder" in failed
    assert "codellama" in installed
    assert "starcoder" in installed
    assert "wizardcoder" in installed
    assert len(failed) == 1
    assert len(installed) == 3


def test_install_category_respects_max_concurrent():
    catalog = DummyCatalogAdapter()
    tracking_adapter = ConcurrencyTrackingRuntimeAdapter()
    manager = LoomcastManager(catalog=catalog)
    manager.runtimes[RuntimeType.OLLAMA] = tracking_adapter

    # 4 models in category 'code', max_concurrent=2
    installed, failed = manager.install_category(
        "code", runtime_type=RuntimeType.OLLAMA, max_concurrent=2
    )

    assert len(installed) == 4
    assert len(failed) == 0
    assert tracking_adapter.max_active_observed <= 2
    assert tracking_adapter.max_active_observed > 0
