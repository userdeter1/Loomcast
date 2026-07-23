# Note on GitHub Actions CI:
# These integration tests require a local Ollama server to be running.
# They do not run in standard CI, to avoid failing on runners with no server.
# To run them in CI later, add a separate GitHub Actions job that installs and
# starts the Ollama daemon on the runner
# (e.g. `curl -fsSL https://ollama.com/install.sh | sh`).

import pytest

from loomcast.adapters.runtimes.ollama import OllamaRuntime

pytestmark = pytest.mark.integration


@pytest.fixture
def ollama_adapter() -> OllamaRuntime:
    adapter = OllamaRuntime()
    if not adapter.is_available():
        pytest.skip("Ollama not detected locally, skipping integration test")
    return adapter


def test_ollama_live_is_available(ollama_adapter: OllamaRuntime) -> None:
    """Check that a real Ollama server responds to is_available()."""
    assert ollama_adapter.is_available() is True


def test_ollama_live_install_and_chat(ollama_adapter: OllamaRuntime) -> None:
    """Install a lightweight model and send a real chat message."""
    # Very small model, to keep the test fast
    model_name = "qwen2.5:0.5b"

    # 1. Install / pull the model
    ollama_adapter.install(model_name)
    assert ollama_adapter.is_model_installed(model_name) is True

    # 2. Send a real message
    messages = [{"role": "user", "content": "Just say 'OK' to validate the test."}]
    response = ollama_adapter.chat(model_name, messages)

    # 3. Check the response is not empty
    assert isinstance(response, str)
    assert len(response.strip()) > 0
