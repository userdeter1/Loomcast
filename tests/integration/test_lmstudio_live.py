# Note CI GitHub Actions:
# Ces tests d'intégration nécessitent un serveur local LM Studio en cours d'exécution.
# Ils ne s'exécutent pas dans la CI automatique standard afin d'éviter d'échouer sur des runners sans serveur.
# Pour les exécuter à l'avenir en CI, il faudrait ajouter un job GitHub Actions séparé
# configurant un serveur local OpenAI-compatible ou LM Studio headless.

import pytest
from loomcast.adapters.runtimes.lmstudio import LMStudioRuntime

pytestmark = pytest.mark.integration


@pytest.fixture
def lmstudio_adapter() -> LMStudioRuntime:
    adapter = LMStudioRuntime()
    if not adapter.is_available():
        pytest.skip("LM Studio non détecté en local, test d'intégration ignoré")
    return adapter


def test_lmstudio_live_is_available(lmstudio_adapter: LMStudioRuntime) -> None:
    """Vérifie qu'un serveur LM Studio réel répond sur is_available()."""
    assert lmstudio_adapter.is_available() is True


def test_lmstudio_live_list_and_chat(lmstudio_adapter: LMStudioRuntime) -> None:
    """Vérifie l'interaction de chat avec un modèle chargé dans LM Studio."""
    models = lmstudio_adapter.list_installed()
    if not models:
        pytest.skip("Aucun modèle chargé dans l'application LM Studio")

    target_model = models[0]
    messages = [{"role": "user", "content": "Dis 'OK' pour valider."}]
    response = lmstudio_adapter.chat(target_model, messages)

    assert isinstance(response, str)
    assert len(response.strip()) > 0
