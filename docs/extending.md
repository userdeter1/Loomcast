# Extension de Loomcast : Ajouter un Nouveau Runtime

Loomcast est conçu selon les principes de la **Clean Architecture** (ports et adaptateurs). Cette architecture permet d'ajouter un nouveau runtime LLM (par exemple vLLM, Text Generation WebUI, LocalAI, etc.) de façon très modulaire sans impacter la logique cœur de l'application.

---

## 1. Le Protocole `RuntimePort`

Toutes les interactions avec les runtimes LLM passent par le port `RuntimePort` défini dans [`loomcast/ports/runtime.py`](../loomcast/ports/runtime.py).

Voici la définition du protocole Python :

```python
from typing import Any, Dict, List, Optional
from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class RuntimePort(Protocol):
    """Abstract port definition for local LLM runtime interactions."""

    def is_available(self) -> bool:
        """Vérifie si le daemon/serveur local est en cours d'exécution et joignable."""
        ...

    def is_model_installed(self, model: str) -> bool:
        """Vérifie si un modèle spécifique est disponible/chargé dans ce runtime."""
        ...

    def install(self, model: str, progress: Optional[Any] = None) -> None:
        """Télécharge ou charge un modèle dans le runtime local."""
        ...

    def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
        """Envoie une liste de messages et retourne le texte généré."""
        ...

    def list_installed(self) -> List[str]:
        """Liste les noms de tous les modèles installés/disponibles."""
        ...
```

---

## 2. Exemple de Référence : `LlamaCppRuntime`

L'adaptateur le plus récent et le plus simple à prendre comme modèle est [`loomcast/adapters/runtimes/llamacpp.py`](../loomcast/adapters/runtimes/llamacpp.py).

Voici une version simplifiée illustrant l'implémentation :

```python
from typing import Any, Dict, List, Optional
import httpx
from loomcast.common.exceptions import RuntimeExecutionError, RuntimeUnavailableError
from loomcast.ports.runtime import RuntimePort


class CustomRuntime(RuntimePort):
    def __init__(self, base_url: str = "http://localhost:5000", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/health", timeout=2.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def list_installed(self) -> List[str]:
        if not self.is_available():
            raise RuntimeUnavailableError("custom", self.base_url)
        # Interroger l'API du runtime
        ...

    def is_model_installed(self, model: str) -> bool:
        return model in self.list_installed()

    def install(self, model: str, progress: Optional[Any] = None) -> None:
        # Télécharger ou valider la présence du modèle
        ...

    def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
        # Envoyer la requête de génération
        ...
```

---

## 3. Étapes pour Intégrer un 4ème Runtime

Pour ajouter un nouveau runtime (ex: `vllm`), suivez ces étapes :

### Étape 1 : Déclarer le type dans le Domaine
Ajoutez la valeur d'énumération dans `loomcast/domain/entities.py` :

```python
class RuntimeType(str, Enum):
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    LLAMACPP = "llamacpp"
    VLLM = "vllm"  # Nouveau runtime
```

### Étape 2 : Ajouter l'URL de configuration
Ajoutez le paramètre et son mapping d'environnement dans `loomcast/common/config.py` :

```python
class LoomcastConfig(BaseModel):
    # ...
    vllm_url: str = Field(default="http://localhost:8000")
```

### Étape 3 : Créer l'Adaptateur
Créez le fichier `loomcast/adapters/runtimes/vllm.py` qui implémente `RuntimePort`.

### Étape 4 : Enregistrer l'Adaptateur dans `LoomcastManager`
Mettez à jour le dictionnaire `self.runtimes` dans `loomcast/core/manager.py` :

```python
self.runtimes = {
    RuntimeType.OLLAMA: OllamaRuntime(base_url=self.config.ollama_url),
    RuntimeType.LMSTUDIO: LMStudioRuntime(base_url=self.config.lmstudio_url),
    RuntimeType.LLAMACPP: LlamaCppRuntime(base_url=self.config.llamacpp_url),
    RuntimeType.VLLM: VllmRuntime(base_url=self.config.vllm_url),
}
```

---

## 4. Règle Stricte de Clean Architecture

> [!IMPORTANT]
> **Séparation des responsabilités** : Ne faites **JAMAIS** dépendre la couche `domain/` ou la couche `ports/` d'une bibliothèque réseau ou E/S tierce (telle que `httpx`, `requests`, `aiohttp`, etc.).

- La couche **Domain** (`loomcast/domain/`) contient uniquement des entités pures (dataclasses / Pydantic models).
- La couche **Ports** (`loomcast/ports/`) contient uniquement des interfaces / protocole de types.
- Toute la logique réseau et les appels HTTP doivent résider exclusivement dans la couche **Adapters** (`loomcast/adapters/runtimes/`).
