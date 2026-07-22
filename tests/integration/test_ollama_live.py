# Note CI GitHub Actions:
# Ces tests d'intégration nécessitent un serveur local Ollama en cours d'exécution.
# Ils ne s'exécutent pas dans la CI automatique standard afin d'éviter d'échouer sur des runners sans serveur.
# Pour les exécuter à l'avenir en CI, il faudrait ajouter un job GitHub Actions séparé
# qui installe et démarre le démon Ollama dans le runner (ex: `curl -fsSL https://ollama.com/install.sh | sh`).

import pytest
from loomcast.adapters.runtimes.ollama import OllamaRuntime

pytestmark = pytest.mark.integration


@pytest.fixture
def ollama_adapter() -> OllamaRuntime:
    adapter = OllamaRuntime()
    if not adapter.is_available():
        pytest.skip("Ollama non détecté en local, test d'intégration ignoré")
    return adapter


def test_ollama_live_is_available(ollama_adapter: OllamaRuntime) -> None:
    """Vérifie qu'un serveur Ollama réel répond sur is_available()."""
    assert ollama_adapter.is_available() is True


def test_ollama_live_install_and_chat(ollama_adapter: OllamaRuntime) -> None:
    """Teste l'installation d'un modèle léger et l'envoi d'un message de chat réel."""
    # Modèle très léger pour des tests rapides
    model_name = "qwen2.5:0.5b"
    
    # 1. Installation / Pull du modèle
    ollama_adapter.install(model_name)
    assert ollama_adapter.is_model_installed(model_name) is True

    # 2. Envoi d'un message réel
    messages = [{"role": "user", "content": "Dis simplement 'OK' pour valider le test."}]
    response = ollama_adapter.chat(model_name, messages)

    # 3. Vérification de la réponse non vide
    assert isinstance(response, str)
    assert len(response.strip()) > 0
