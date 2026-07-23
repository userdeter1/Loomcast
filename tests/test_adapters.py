import httpx
import pytest
from loomcast.adapters.runtimes.llamacpp import LlamaCppRuntime
from loomcast.adapters.runtimes.lmstudio import LMStudioRuntime
from loomcast.adapters.runtimes.ollama import OllamaRuntime
from loomcast.common.exceptions import (
    ModelNotFoundError,
    RuntimeExecutionError,
    RuntimeUnavailableError,
)
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
        return httpx.Response(
            200,
            json={"models": [{"name": "llama3:latest"}, {"name": "mistral:latest"}]},
        )

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
            return httpx.Response(
                200,
                json={
                    "message": {"role": "assistant", "content": "Hello from Ollama!"}
                },
            )
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
            return httpx.Response(
                200,
                json={
                    "data": [{"id": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"}]
                },
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = LMStudioRuntime(base_url="http://localhost:1234")

    monkeypatch.setattr("httpx.get", client.get)
    assert runtime.is_available() is True
    assert runtime.list_installed() == [
        "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
    ]


def test_lmstudio_chat_success(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": "local-model"}]})
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "Hello from LM Studio!"}}]},
            )
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


def test_llamacpp_runtime_protocol_instance():
    runtime = LlamaCppRuntime()
    assert isinstance(runtime, RuntimePort)


def test_llamacpp_is_available_and_models(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/v1/models":
            return httpx.Response(
                200, json={"data": [{"id": "llama-2-7b.Q4_K_M.gguf"}]}
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = LlamaCppRuntime(base_url="http://localhost:8080")

    monkeypatch.setattr("httpx.get", client.get)
    assert runtime.is_available() is True
    assert runtime.list_installed() == ["llama-2-7b.Q4_K_M.gguf"]
    assert runtime.is_model_installed("llama-2-7b.Q4_K_M.gguf") is True
    assert runtime.is_model_installed("nonexistent") is False


def test_llamacpp_chat_success(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "Hello from llama.cpp!"}}]},
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = LlamaCppRuntime(base_url="http://localhost:8080")

    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.post", client.post)

    response = runtime.chat(
        "llama-2-7b.Q4_K_M.gguf", [{"role": "user", "content": "Hi"}]
    )
    assert response == "Hello from llama.cpp!"


def test_llamacpp_install_raises_explanatory_error(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": "loaded-model"}]})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = LlamaCppRuntime(base_url="http://localhost:8080")

    monkeypatch.setattr("httpx.get", client.get)

    with pytest.raises(RuntimeExecutionError) as exc_info:
        runtime.install("unloaded-model")

    assert "llama-server" in str(exc_info.value)


def test_ollama_remove_success(monkeypatch):
    deleted_payload = {}

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "llama3:latest"}]})
        if request.url.path == "/api/delete" and request.method == "DELETE":
            import json

            deleted_payload.update(json.loads(request.content.decode("utf-8")))
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.request", client.request)

    runtime.remove("llama3")
    assert deleted_payload == {"name": "llama3"}


def test_ollama_remove_model_not_found(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "llama3:latest"}]})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)

    with pytest.raises(ModelNotFoundError) as exc_info:
        runtime.remove("nonexistent")
    assert "nonexistent" in str(exc_info.value)


def test_lmstudio_remove_raises_explanatory_error():
    runtime = LMStudioRuntime()
    with pytest.raises(RuntimeExecutionError) as exc_info:
        runtime.remove("any-model")
    assert "LM Studio" in str(exc_info.value)


def test_llamacpp_remove_raises_explanatory_error():
    runtime = LlamaCppRuntime()
    with pytest.raises(RuntimeExecutionError) as exc_info:
        runtime.remove("any-model")
    assert "llama-server" in str(exc_info.value)


def test_ollama_update_digest_changed(monkeypatch):
    pulled = False

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal pulled
        if request.url.path == "/api/tags":
            digest = "sha256:v2" if pulled else "sha256:v1"
            return httpx.Response(
                200, json={"models": [{"name": "llama3:latest", "digest": digest}]}
            )
        if request.url.path == "/api/pull":
            pulled = True
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.post", client.post)

    updated = runtime.update("llama3")
    assert updated is True


def test_ollama_update_digest_unchanged(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={"models": [{"name": "llama3:latest", "digest": "sha256:same"}]},
            )
        if request.url.path == "/api/pull":
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.post", client.post)

    updated = runtime.update("llama3")
    assert updated is False


def test_ollama_update_model_not_found(monkeypatch):
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "llama3:latest"}]})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    runtime = OllamaRuntime(base_url="http://localhost:11434")

    monkeypatch.setattr("httpx.get", client.get)

    with pytest.raises(ModelNotFoundError) as exc_info:
        runtime.update("nonexistent")
    assert "nonexistent" in str(exc_info.value)


def test_lmstudio_update_raises_explanatory_error(monkeypatch):
    runtime = LMStudioRuntime()
    monkeypatch.setattr(runtime, "is_available", lambda: True)
    with pytest.raises(RuntimeExecutionError) as exc_info:
        runtime.update("any-model")
    assert "LM Studio" in str(exc_info.value)


def test_llamacpp_update_raises_explanatory_error(monkeypatch):
    runtime = LlamaCppRuntime()
    monkeypatch.setattr(runtime, "is_available", lambda: True)
    with pytest.raises(RuntimeExecutionError) as exc_info:
        runtime.update("any-model")
    assert "llama-server" in str(exc_info.value)
