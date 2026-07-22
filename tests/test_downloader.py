from unittest.mock import MagicMock, call
import httpx
from rich.console import Console

from loomcast.adapters.downloader.progress import (
    NullProgressReporter,
    ProgressReporter,
    RichProgressReporter,
)
from loomcast.adapters.runtimes.ollama import OllamaRuntime


def test_null_progress_reporter():
    reporter = NullProgressReporter()
    # Should perform no-op and raise no errors
    reporter.on_progress("downloading", 100, 1000)
    reporter.on_progress("verifying sha256 digest", None, None)


def test_rich_progress_reporter_normal_and_none_values():
    console = Console(quiet=True)
    reporter = RichProgressReporter(console=console)

    # Test normal values
    reporter.on_progress("pulling manifest", 0, 100)
    reporter.on_progress("downloading layer", 50, 100)
    reporter.on_progress("downloading layer", 100, 100)

    # Test graceful handling of completed/total as None (e.g. "verifying sha256 digest")
    reporter.on_progress("verifying sha256 digest", None, None)
    reporter.on_progress("writing manifest", None, None)

    # Clean up
    reporter.stop()


def test_rich_progress_reporter_context_manager():
    console = Console(quiet=True)
    with RichProgressReporter(console=console) as reporter:
        reporter.on_progress("status 1", 10, 20)
        reporter.on_progress("verifying sha256 digest", None, None)


def test_ollama_runtime_install_with_progress_reporter_streaming(monkeypatch):
    ndjson_content = (
        b'{"status": "pulling manifest"}\n'
        b'{"status": "downloading digestname", "completed": 500, "total": 1000}\n'
        b'{"status": "verifying sha256 digest"}\n'
        b'{"status": "success"}\n'
    )

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        if request.url.path == "/api/pull":
            return httpx.Response(200, content=ndjson_content)
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.stream", client.stream)

    runtime = OllamaRuntime(base_url="http://localhost:11434")
    mock_reporter = MagicMock(spec=ProgressReporter)

    runtime.install("llama3", progress=mock_reporter)

    assert mock_reporter.on_progress.call_count == 4
    mock_reporter.on_progress.assert_has_calls([
        call("pulling manifest", None, None),
        call("downloading digestname", 500, 1000),
        call("verifying sha256 digest", None, None),
        call("success", None, None),
    ])


def test_ollama_runtime_install_without_progress_reporter(monkeypatch):
    post_calls = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        if request.url.path == "/api/pull":
            post_calls.append(request)
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    monkeypatch.setattr("httpx.get", client.get)
    monkeypatch.setattr("httpx.post", client.post)

    runtime = OllamaRuntime(base_url="http://localhost:11434")

    # Install without progress reporter
    runtime.install("llama3")

    assert len(post_calls) == 1
    assert post_calls[0].url.path == "/api/pull"
