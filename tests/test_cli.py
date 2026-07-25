import pytest
from typer.testing import CliRunner

from loomcast.cli.main import app
from loomcast.domain.entities import CatalogEntry, RuntimeType, VerificationResult

runner = CliRunner()


def test_cli_status(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        config = type(
            "Config",
            (),
            {
                "default_backend": RuntimeType.OLLAMA,
                "ollama_url": "http://localhost:11434",
                "lmstudio_url": "http://localhost:1234",
                "llamacpp_url": "http://localhost:8080",
            },
        )()

        def list_available_runtimes(self):
            return {
                RuntimeType.OLLAMA: True,
                RuntimeType.LMSTUDIO: False,
                RuntimeType.LLAMACPP: False,
            }

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "ONLINE" in result.output.upper()
    assert "OFFLINE" in result.output.upper()


def test_cli_list(monkeypatch: pytest.MonkeyPatch):
    class MockAdapter:
        def is_available(self):
            return True

        def list_installed(self):
            return ["llama3:latest"]

    class MockManager:
        def get_runtime(self, rtype):
            return MockAdapter()

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "llama3:latest" in result.output


def test_cli_search(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        def search(self, query):
            return [
                CatalogEntry(
                    name="codellama",
                    description="Code generation model",
                    publisher="meta",
                    tags=["code"],
                    default_runtime=RuntimeType.OLLAMA,
                )
            ]

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["search", "code"])
    assert result.exit_code == 0
    assert "codellama" in result.output


def test_cli_recommend(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        def recommend(self, task):
            return [
                CatalogEntry(
                    name="deepseek-coder",
                    description="DeepSeek coder model",
                    publisher="deepseek",
                    tags=["code"],
                    default_runtime=RuntimeType.OLLAMA,
                )
            ]

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["recommend", "code"])
    assert result.exit_code == 0
    assert "deepseek-coder" in result.output


def test_cli_install_category(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        def install_category(self, category, runtime_type=None, **kwargs):
            return (["codellama"], ["deepseek-coder"])

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["install-category", "code"])
    assert result.exit_code == 0
    assert "Category installation complete!" in result.output
    assert "codellama" in result.output
    assert "deepseek-coder" in result.output


def test_cli_install_category_sequential(monkeypatch: pytest.MonkeyPatch):
    passed_args = {}

    class MockManager:
        def install_category(
            self, category, runtime_type=None, max_concurrent=3, progress=None
        ):
            passed_args["max_concurrent"] = max_concurrent
            return (["codellama"], [])

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["install-category", "code", "--sequential"])
    assert result.exit_code == 0
    assert passed_args["max_concurrent"] == 1


def test_cli_verify(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        def verify(self, model, runtime_type=None):
            return VerificationResult(
                model=model,
                runtime_type=RuntimeType.OLLAMA,
                verified=True,
                digest="sha256:123456",
                message="Integrity verified",
            )

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["verify", "llama3"])
    assert result.exit_code == 0
    assert "llama3" in result.output
    assert "sha256:123456" in result.output


def test_cli_remove_interactive_confirm(monkeypatch: pytest.MonkeyPatch):
    removed = []

    class MockManager:
        def remove(self, model, runtime_type=None):
            removed.append((model, runtime_type))

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["remove", "llama3"], input="y\n")
    assert result.exit_code == 0
    assert removed == [("llama3", None)]
    assert "Successfully removed model" in result.output


def test_cli_remove_interactive_abort(monkeypatch: pytest.MonkeyPatch):
    removed = []

    class MockManager:
        def remove(self, model, runtime_type=None):
            removed.append((model, runtime_type))

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["remove", "llama3"], input="n\n")
    assert result.exit_code != 0
    assert len(removed) == 0


def test_cli_remove_yes_flag(monkeypatch: pytest.MonkeyPatch):
    removed = []

    class MockManager:
        def remove(self, model, runtime_type=None):
            removed.append((model, runtime_type))

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["remove", "llama3", "--yes", "-b", "ollama"])
    assert result.exit_code == 0
    assert removed == [("llama3", "ollama")]
    assert "Successfully removed model" in result.output


def test_cli_update_success(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        def update(self, model, runtime_type=None, progress=None):
            return True

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["update", "llama3"])
    assert result.exit_code == 0
    assert "Successfully updated model" in result.output


def test_cli_update_already_latest(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        def update(self, model, runtime_type=None, progress=None):
            return False

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["update", "llama3"])
    assert result.exit_code == 0
    assert "Already up to date, nothing to do" in result.output


def test_cli_doctor_all_runtimes_available(monkeypatch: pytest.MonkeyPatch):
    from loomcast.adapters.catalog.static import StaticCatalog

    class MockManager:
        config = type(
            "Config",
            (),
            {"default_backend": RuntimeType.OLLAMA},
        )()
        catalog = StaticCatalog()

        def list_available_runtimes(self):
            return {
                RuntimeType.OLLAMA: True,
                RuntimeType.LMSTUDIO: True,
                RuntimeType.LLAMACPP: True,
            }

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "0 problem(s) found" in result.output


def test_cli_doctor_default_backend_offline(monkeypatch: pytest.MonkeyPatch):
    from loomcast.adapters.catalog.static import StaticCatalog

    class MockManager:
        config = type(
            "Config",
            (),
            {"default_backend": RuntimeType.OLLAMA},
        )()
        catalog = StaticCatalog()

        def list_available_runtimes(self):
            return {
                RuntimeType.OLLAMA: False,
                RuntimeType.LMSTUDIO: True,
                RuntimeType.LLAMACPP: True,
            }

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code != 0
    assert "1 problem(s) found" in result.output


def test_cli_doctor_dynamic_catalog_fallback_warning(monkeypatch: pytest.MonkeyPatch):
    from loomcast.adapters.catalog.dynamic import DynamicCatalog
    from loomcast.adapters.catalog.static import StaticCatalog

    class MockDynamicCatalog(DynamicCatalog):
        def __init__(self):
            self.fallback_catalog = StaticCatalog()

        def _get_entries(self):
            return None, True

    class MockManager:
        config = type(
            "Config",
            (),
            {"default_backend": RuntimeType.OLLAMA},
        )()
        catalog = MockDynamicCatalog()

        def list_available_runtimes(self):
            return {
                RuntimeType.OLLAMA: True,
                RuntimeType.LMSTUDIO: True,
                RuntimeType.LLAMACPP: True,
            }

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "0 problem(s) found" in result.output
    assert "1 warning(s)" in result.output


def test_cli_doctor_static_catalog_checksum_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    from loomcast.adapters.catalog.static import StaticCatalog

    real_static = StaticCatalog()
    catalog_json_content = real_static.catalog_path.read_bytes()

    bad_catalog = tmp_path / "catalog.json"
    bad_catalog.write_bytes(catalog_json_content)
    bad_sha = tmp_path / "catalog.json.sha256"
    bad_sha.write_text("invalid_checksum_hash_12345")

    class MockManager:
        config = type(
            "Config",
            (),
            {"default_backend": RuntimeType.OLLAMA},
        )()
        catalog = real_static

        def list_available_runtimes(self):
            return {
                RuntimeType.OLLAMA: True,
                RuntimeType.LMSTUDIO: True,
                RuntimeType.LLAMACPP: True,
            }

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    monkeypatch.setattr(
        "loomcast.cli.main.StaticCatalog",
        lambda *args, **kwargs: StaticCatalog(catalog_path=bad_catalog),
    )

    result = runner.invoke(app, ["doctor"])
    assert result.exit_code != 0
    assert "1 problem(s) found" in result.output


# --- Rich markup safety -------------------------------------------------------
# Model output, catalog descriptions and runtime model names are external data.
# Rendering them as rich markup let a response containing an unmatched closing
# tag (e.g. "[/path]") raise MarkupError and print a raw traceback.

MARKUP_PAYLOAD = "see [/unmatched] and [bold red]styled[/bold red]"


def test_cli_chat_renders_markup_in_response_literally(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        def chat(self, model, messages, runtime_type=None):
            return MARKUP_PAYLOAD

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["chat", "m", "hi"])

    assert result.exit_code == 0
    assert result.exception is None
    # The tags survive as text instead of being consumed as styling.
    assert "[/unmatched]" in result.output
    assert "[bold red]" in result.output


def test_cli_search_survives_markup_in_catalog_description(
    monkeypatch: pytest.MonkeyPatch,
):
    class MockManager:
        def search(self, query):
            return [
                CatalogEntry(
                    name="evil-model",
                    description=MARKUP_PAYLOAD,
                    publisher="ollama",
                    tags=["[/oops]"],
                    default_runtime=RuntimeType.OLLAMA,
                )
            ]

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["search", "evil"])

    assert result.exit_code == 0
    assert result.exception is None
    assert "evil-model" in result.output


def test_cli_list_survives_markup_in_model_name(monkeypatch: pytest.MonkeyPatch):
    class MockAdapter:
        def is_available(self):
            return True

        def list_installed(self):
            return ["weird[/name]:latest"]

    class MockManager:
        def get_runtime(self, rtype):
            return MockAdapter()

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert result.exception is None


# --- compare command ----------------------------------------------------------
from loomcast.domain.entities import ComparisonResult  # noqa: E402


def _compare_manager(results):
    class MockManager:
        def compare(self, prompt, runtime_types=None, model=None):
            self.called_with = (prompt, runtime_types, model)
            return results

    return MockManager()


def test_cli_compare_shows_each_runtime(monkeypatch: pytest.MonkeyPatch):
    results = [
        ComparisonResult(
            runtime_type=RuntimeType.OLLAMA, model="llama3", response="hi from ollama"
        ),
        ComparisonResult(
            runtime_type=RuntimeType.LMSTUDIO, available=False, error="Runtime offline"
        ),
    ]
    monkeypatch.setattr(
        "loomcast.cli.main.get_manager", lambda: _compare_manager(results)
    )
    result = runner.invoke(app, ["compare", "hello"])

    assert result.exit_code == 0
    assert "OLLAMA" in result.output
    assert "llama3" in result.output
    assert "LMSTUDIO" in result.output
    assert "Runtime offline" in result.output


def test_cli_compare_renders_markup_in_response_literally(
    monkeypatch: pytest.MonkeyPatch,
):
    results = [
        ComparisonResult(
            runtime_type=RuntimeType.OLLAMA,
            model="llama3",
            response="see [/path] and [bold red]x[/bold red]",
        )
    ]
    monkeypatch.setattr(
        "loomcast.cli.main.get_manager", lambda: _compare_manager(results)
    )
    result = runner.invoke(app, ["compare", "hello"])

    assert result.exit_code == 0
    assert result.exception is None
    assert "[/path]" in result.output
    assert "[bold red]" in result.output


def test_cli_compare_exit_code_when_no_response(monkeypatch: pytest.MonkeyPatch):
    results = [
        ComparisonResult(
            runtime_type=RuntimeType.OLLAMA, available=False, error="Runtime offline"
        ),
        ComparisonResult(
            runtime_type=RuntimeType.LMSTUDIO, available=False, error="Runtime offline"
        ),
    ]
    monkeypatch.setattr(
        "loomcast.cli.main.get_manager", lambda: _compare_manager(results)
    )
    result = runner.invoke(app, ["compare", "hello"])

    assert result.exit_code == 1


def test_cli_compare_forwards_backend_filter(monkeypatch: pytest.MonkeyPatch):
    mgr = _compare_manager(
        [ComparisonResult(runtime_type=RuntimeType.OLLAMA, model="m", response="ok")]
    )
    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: mgr)
    result = runner.invoke(
        app, ["compare", "hi", "-b", "ollama", "-b", "lmstudio", "-m", "shared"]
    )

    assert result.exit_code == 0
    prompt, runtime_types, model = mgr.called_with
    assert prompt == "hi"
    assert runtime_types == ["ollama", "lmstudio"]
    assert model == "shared"
