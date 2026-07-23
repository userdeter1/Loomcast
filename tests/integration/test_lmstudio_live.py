# Note on GitHub Actions CI:
# These integration tests require a local LM Studio server to be running.
# They do not run in standard CI, to avoid failing on runners with no server.
# To run them in CI later, add a separate GitHub Actions job that sets up a
# local OpenAI-compatible server or a headless LM Studio.

import pytest

from loomcast.adapters.runtimes.lmstudio import LMStudioRuntime

pytestmark = pytest.mark.integration


@pytest.fixture
def lmstudio_adapter() -> LMStudioRuntime:
    adapter = LMStudioRuntime()
    if not adapter.is_available():
        pytest.skip("LM Studio not detected locally, skipping integration test")
    return adapter


def test_lmstudio_live_is_available(lmstudio_adapter: LMStudioRuntime) -> None:
    """Check that a real LM Studio server responds to is_available()."""
    assert lmstudio_adapter.is_available() is True


def test_lmstudio_live_list_and_chat(lmstudio_adapter: LMStudioRuntime) -> None:
    """Check chat interaction with a model loaded in LM Studio."""
    models = lmstudio_adapter.list_installed()
    if not models:
        pytest.skip("No model loaded in the LM Studio application")

    target_model = models[0]
    messages = [{"role": "user", "content": "Say 'OK' to validate."}]
    response = lmstudio_adapter.chat(target_model, messages)

    assert isinstance(response, str)
    assert len(response.strip()) > 0
