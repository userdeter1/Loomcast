import pytest
from typer.testing import CliRunner

from loomcast.cli.main import app
from loomcast.domain.entities import CatalogEntry, RuntimeType, VerificationResult

runner = CliRunner()


def test_cli_status(monkeypatch: pytest.MonkeyPatch):
    class MockManager:
        config = type("Config", (), {"default_backend": RuntimeType.OLLAMA, "ollama_url": "http://localhost:11434", "lmstudio_url": "http://localhost:1234"})()

        def list_available_runtimes(self):
            return {RuntimeType.OLLAMA: True, RuntimeType.LMSTUDIO: False}

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
        def install_category(self, category, runtime_type=None):
            return (["codellama"], ["deepseek-coder"])

    monkeypatch.setattr("loomcast.cli.main.get_manager", lambda: MockManager())
    result = runner.invoke(app, ["install-category", "code"])
    assert result.exit_code == 0
    assert "Category installation complete!" in result.output
    assert "codellama" in result.output
    assert "deepseek-coder" in result.output


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
