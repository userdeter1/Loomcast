import httpx
import pytest
from loomcast.adapters.runtimes.lmstudio import LMStudioRuntime
from loomcast.adapters.runtimes.ollama import OllamaRuntime
from loomcast.common.exceptions import RuntimeExecutionError, RuntimeUnavailableError
from loomcast.ports.runtime import RuntimePort


def test_ollama_runtime_protocol_instance():
    runtime = OllamaRuntime()
    assert isinstance(runtime, RuntimePort)


def test_lmstudio_runtime_protocol_instance():
    runtime = LMStudioRuntime()
    assert isinstance(runtime, RuntimePort)


def test_ollama_is_available_success(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    # Patch httpx.get inside adapter to use mock transport
    monkeypatch.setattr("httpx.get", client.get)
    assert runtime.is_available() is True


def test_ollama_list_installed(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"models": [{"name": "llama3:latest"}, {"name": "mistral:latest"}]})

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)
    installed = runtime.list_installed()
    assert installed == ["llama3:latest", "mistral:latest"]
    assert runtime.is_model_installed("llama3") is True
    assert runtime.is_model_installed("nonexistent") is False


def test_ollama_chat_success(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        if request.url.path == "/api/chat":
            return httpx.Response(200, json={"message": {"role": "assistant", "content": "Hello from Ollama!"}})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.post", client.post)

    response = runtime.chat("llama3", [{"role": "user", "content": "Hello!"}])
    assert response == "Hello from Ollama!"


def test_lmstudio_is_available_success(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"}]})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = LMStudioRuntime(base_url="http://localhost:1234")

    monkeypatch.setattr("httpx.get", client.get)
    assert runtime.is_available() is True
    assert runtime.list_installed() == ["lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"]


def test_lmstudio_chat_success(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": "local-model"}]})
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(200, json={"choices": [{"message": {"content": "Hello from LM Studio!"}}]})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = LMStudioRuntime(base_url="http://localhost:1234")

    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.post", client.post)

    response = runtime.chat("local-model", [{"role": "user", "content": "Hi"}])
    assert response == "Hello from LM Studio!"


def test_runtime_unavailable_exception(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)
    assert runtime.is_available() is False
    with pytest.raises(RuntimeUnavailableError):
        runtime.list_installed()
