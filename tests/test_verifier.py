import httpx
import pytest

from loomcast.adapters.runtimes.lmstudio import LMStudioRuntime
from loomcast.adapters.runtimes.ollama import OllamaRuntime
from loomcast.common.exceptions import ModelNotFoundError
from loomcast.core.manager import LoomcastManager
from loomcast.core.verifier import ModelVerifier
from loomcast.domain.entities import RuntimeType


def test_verify_ollama_model_with_digest(monkeypatch: pytest.MonkeyPatch):
    """Test verify() on Ollama model with valid digest present returns verified=True."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": "llama3:latest",
                            "digest": "sha256:abc123def4567890",
                        }
                    ]
                },
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    ollama_adapter = OllamaRuntime(base_url="http://localhost:11434")
    monkeypatch.setattr("httpx.get", client.get)

    verifier = ModelVerifier(runtimes={RuntimeType.OLLAMA: ollama_adapter})
    result = verifier.verify("llama3", RuntimeType.OLLAMA)

    assert result.model == "llama3"
    assert result.runtime_type == RuntimeType.OLLAMA
    assert result.verified is True
    assert result.digest == "sha256:abc123def4567890"
    assert "verified" in result.message.lower()


def test_verify_ollama_model_missing_digest(monkeypatch: pytest.MonkeyPatch):
    """Test verify() on Ollama model with missing/empty digest returns verified=False."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": "mistral:latest",
                            "digest": "",
                        }
                    ]
                },
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    ollama_adapter = OllamaRuntime(base_url="http://localhost:11434")
    monkeypatch.setattr("httpx.get", client.get)

    verifier = ModelVerifier(runtimes={RuntimeType.OLLAMA: ollama_adapter})
    result = verifier.verify("mistral", RuntimeType.OLLAMA)

    assert result.model == "mistral"
    assert result.runtime_type == RuntimeType.OLLAMA
    assert result.verified is False
    assert result.digest is None
    assert "missing or empty" in result.message.lower()


def test_verify_lmstudio_model(monkeypatch: pytest.MonkeyPatch):
    """Test verify() on LM Studio returns verified=False with explanatory message."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/models":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {"id": "meta-llama-3-8b-instruct"}
                    ]
                },
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    lmstudio_adapter = LMStudioRuntime(base_url="http://localhost:1234")
    monkeypatch.setattr("httpx.get", client.get)

    verifier = ModelVerifier(runtimes={RuntimeType.LMSTUDIO: lmstudio_adapter})
    result = verifier.verify("meta-llama-3-8b-instruct", RuntimeType.LMSTUDIO)

    assert result.model == "meta-llama-3-8b-instruct"
    assert result.runtime_type == RuntimeType.LMSTUDIO
    assert result.verified is False
    assert result.digest is None
    assert "LM Studio n'expose pas de digest vérifiable" in result.message


def test_verify_non_installed_model_raises_exception(monkeypatch: pytest.MonkeyPatch):
    """Test verify() on a non-installed model raises ModelNotFoundError."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    ollama_adapter = OllamaRuntime(base_url="http://localhost:11434")
    monkeypatch.setattr("httpx.get", client.get)

    verifier = ModelVerifier(runtimes={RuntimeType.OLLAMA: ollama_adapter})
    with pytest.raises(ModelNotFoundError) as exc_info:
        verifier.verify("nonexistent-model", RuntimeType.OLLAMA)

    assert "nonexistent-model" in str(exc_info.value)


def test_loomcast_manager_verify_integration(monkeypatch: pytest.MonkeyPatch):
    """Test LoomcastManager.verify delegation."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": "codellama:latest",
                            "digest": "sha256:789abc",
                        }
                    ]
                },
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    monkeypatch.setattr("httpx.get", client.get)

    manager = LoomcastManager()
    result = manager.verify("codellama", runtime_type="ollama")

    assert result.verified is True
    assert result.digest == "sha256:789abc"
