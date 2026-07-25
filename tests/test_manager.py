from __future__ import annotations

import threading
import time
from typing import Any

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

    def install(self, model: str, progress: Any | None = None) -> None:
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

    def install(self, model: str, progress: Any | None = None) -> None:
        with self.lock:
            self.active_count += 1
            self.max_active_observed = max(self.max_active_observed, self.active_count)

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


def test_manager_remove_resolve_runtime():
    removed_calls = []

    class MockRuntime(RuntimePort):
        def is_available(self) -> bool:
            return True

        def is_model_installed(self, model: str) -> bool:
            return True

        def install(self, model: str, progress: Any | None = None) -> None:
            pass

        def chat(self, model: str, messages: list) -> str:
            return ""

        def list_installed(self) -> list:
            return []

        def remove(self, model: str) -> None:
            removed_calls.append(model)

    manager = LoomcastManager()
    mock_adapter = MockRuntime()
    manager.runtimes[RuntimeType.LMSTUDIO] = mock_adapter

    manager.remove("llama3", runtime_type="lmstudio")
    assert removed_calls == ["llama3"]


def test_manager_update_resolve_runtime():
    updated_calls = []

    class MockRuntime(RuntimePort):
        def is_available(self) -> bool:
            return True

        def is_model_installed(self, model: str) -> bool:
            return True

        def install(self, model: str, progress: Any | None = None) -> None:
            pass

        def chat(self, model: str, messages: list) -> str:
            return ""

        def list_installed(self) -> list:
            return []

        def remove(self, model: str) -> None:
            pass

        def update(self, model: str, progress: Any | None = None) -> bool:
            updated_calls.append(model)
            return True

    manager = LoomcastManager()
    mock_adapter = MockRuntime()
    manager.runtimes[RuntimeType.OLLAMA] = mock_adapter

    res = manager.update("llama3", runtime_type="ollama")
    assert res is True
    assert updated_calls == ["llama3"]


# --- compare (multi-runtime) --------------------------------------------------
from loomcast.common.exceptions import RuntimeUnavailableError  # noqa: E402


class FakeRuntime(RuntimePort):
    """Configurable runtime double for compare() tests."""

    def __init__(self, available=True, installed=None, reply="ok", fail_chat=False):
        self._available = available
        self._installed = installed if installed is not None else ["auto-model"]
        self._reply = reply
        self._fail_chat = fail_chat
        self.chat_calls: list[tuple[str, str]] = []

    def is_available(self) -> bool:
        return self._available

    def list_installed(self) -> list[str]:
        if not self._available:
            raise RuntimeUnavailableError("fake", "http://x")
        return list(self._installed)

    def is_model_installed(self, model: str) -> bool:
        return model in self._installed

    def chat(self, model: str, messages: list[dict[str, Any]]) -> str:
        if self._fail_chat:
            raise RuntimeExecutionError("chat boom")
        self.chat_calls.append((model, messages[-1]["content"]))
        return f"{self._reply}:{model}"

    def install(self, model, progress=None):  # pragma: no cover - unused here
        ...

    def remove(self, model):  # pragma: no cover - unused here
        ...

    def update(self, model, progress=None):  # pragma: no cover - unused here
        return False


def _manager_with(runtimes: dict) -> LoomcastManager:
    mgr = LoomcastManager(catalog=DummyCatalogAdapter())
    for rtype, adapter in runtimes.items():
        mgr.runtimes[rtype] = adapter
    return mgr


def test_compare_returns_results_in_requested_order():
    mgr = _manager_with(
        {
            RuntimeType.OLLAMA: FakeRuntime(reply="a"),
            RuntimeType.LMSTUDIO: FakeRuntime(reply="b"),
        }
    )
    results = mgr.compare(
        "hi", runtime_types=[RuntimeType.LMSTUDIO, RuntimeType.OLLAMA]
    )
    assert [r.runtime_type for r in results] == [
        RuntimeType.LMSTUDIO,
        RuntimeType.OLLAMA,
    ]
    assert results[0].response == "b:auto-model"
    assert results[1].response == "a:auto-model"
    assert all(r.error is None for r in results)


def test_compare_defaults_to_all_runtimes():
    mgr = _manager_with(
        {
            RuntimeType.OLLAMA: FakeRuntime(),
            RuntimeType.LMSTUDIO: FakeRuntime(),
            RuntimeType.LLAMACPP: FakeRuntime(),
        }
    )
    results = mgr.compare("hi")
    assert {r.runtime_type for r in results} == set(RuntimeType)


def test_compare_offline_runtime_yields_error_not_crash():
    mgr = _manager_with(
        {
            RuntimeType.OLLAMA: FakeRuntime(reply="a"),
            RuntimeType.LMSTUDIO: FakeRuntime(available=False),
        }
    )
    results = mgr.compare("hi", runtime_types=["ollama", "lmstudio"])
    online, offline = results[0], results[1]
    assert online.response == "a:auto-model"
    assert offline.available is False
    assert offline.error == "Runtime offline"
    assert offline.model is None


def test_compare_model_resolution_precedence():
    ollama = FakeRuntime(installed=["installed-first"])
    lmstudio = FakeRuntime(installed=["installed-first"])
    mgr = _manager_with({RuntimeType.OLLAMA: ollama, RuntimeType.LMSTUDIO: lmstudio})
    results = mgr.compare(
        "hi",
        runtime_types=["ollama", "lmstudio"],
        model="shared",
        models={RuntimeType.OLLAMA: "override"},
    )
    # per-runtime override wins for ollama, shared model for lmstudio
    assert results[0].model == "override"
    assert results[1].model == "shared"


def test_compare_auto_detects_first_installed_model():
    mgr = _manager_with({RuntimeType.OLLAMA: FakeRuntime(installed=["m1", "m2"])})
    result = mgr.compare("hi", runtime_types=["ollama"])[0]
    assert result.model == "m1"


def test_compare_no_installed_model_reports_error():
    mgr = _manager_with({RuntimeType.OLLAMA: FakeRuntime(installed=[])})
    result = mgr.compare("hi", runtime_types=["ollama"])[0]
    assert result.response is None
    assert result.error == "No model available on this runtime"


def test_compare_chat_failure_is_isolated():
    mgr = _manager_with(
        {
            RuntimeType.OLLAMA: FakeRuntime(reply="a"),
            RuntimeType.LMSTUDIO: FakeRuntime(fail_chat=True),
        }
    )
    results = mgr.compare("hi", runtime_types=["ollama", "lmstudio"])
    assert results[0].response == "a:auto-model"
    assert results[1].response is None
    assert "chat boom" in results[1].error


def test_compare_deduplicates_repeated_runtime():
    mgr = _manager_with({RuntimeType.OLLAMA: FakeRuntime()})
    results = mgr.compare("hi", runtime_types=["ollama", "ollama"])
    assert len(results) == 1
