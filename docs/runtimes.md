# Runtimes Supportés et Gestion des Backends

Loomcast intègre une couche d'abstraction permettant de gérer de manière unifiée plusieurs serveurs d'exécution LLM locaux (runtimes).

---

## 1. Tableau Comparatif des Runtimes Supportés

| Caractéristique | Ollama | LM Studio | llama.cpp (`llama-server`) |
| :--- | :--- | :--- | :--- |
| **Backend Enum** | `ollama` | `lmstudio` | `llamacpp` |
| **Port par défaut** | `11434` | `1234` | `8080` |
| **Protocole API** | API native REST (`/api/chat`, `/api/pull`, `/api/tags`) | API OpenAI-compatible (`/v1/chat/completions`, `/v1/models`) | API OpenAI-compatible (`/v1/chat/completions`, `/v1/models`, `/health`) |
| **Installation de modèles** | **Automatique** via API (`POST /api/pull`) | **Manuelle** dans l'application LM Studio | **Manuelle** au démarrage du serveur (`llama-server -m`) |
| **Vérification d'intégrité** | **Disponible** (via digest SHA256 renvoyé par l'API Ollama) | **Non disponible** (l'API `/v1/models` n'expose pas de digests) | **Non disponible** (API REST ne fournit pas de digests) |
| **Modèles simultanés** | Plusieurs modèles gérés par l'instance | Selon les capacités configurées dans l'application | **Un seul modèle** chargé à la fois par instance de `llama-server` |

---

## 2. Limitations Connues par Runtime

### Ollama (`ollama`)
- **Points forts** : Support natif du téléchargement de modèles avec suivi de progression en temps réel, vérification complète de l'intégrité via SHA256 digest (`loomcast verify`).

### LM Studio (`lmstudio`)
- **Installation** : LM Studio n'expose pas d'endpoint HTTP public pour télécharger des modèles à distance via API. Les modèles doivent être préalablement recherchés et chargés dans l'interface graphique de LM Studio.
- **Vérification** : La commande `loomcast verify` renvoie un statut non vérifié car l'API OpenAI-compatible de LM Studio n'inclut pas de signatures cryptographiques.

### llama.cpp (`llamacpp`)
- **Modèle unique** : Une instance de `llama-server` est lancée pour servir **un modèle unique** spécifié lors du démarrage de l'exécutable (`-m /path/to/model.gguf`).
- **Installation API** : Pas de téléchargement à chaud via l'API REST. Tenter d'installer un modèle non chargé retournera un message d'erreur invitant à relancer le serveur avec le modèle désiré.

---

## 3. Basculer d'un Runtime à l'Autre

Loomcast permet de basculer facilement d'un backend à un autre via 3 mécanismes distincts.

### A. Via le Flag CLI (`--backend` / `-b`)
Pour surcharger ponctuellement le runtime d'une commande CLI :

```bash
# Vérifier les modèles chargés dans LM Studio
loomcast list --backend lmstudio

# Télécharger un modèle dans Ollama
loomcast install qwen2.5:0.5b -b ollama

# Discuter avec un modèle servi par llama-server
loomcast chat gemma-2-2b "Expose le principe de la Clean Architecture." --backend llamacpp
```

### B. Via le SDK Python (`runtime_type`)
Dans vos scripts Python, passez le paramètre `runtime_type` :

```python
import loomcast

# Requête vers LM Studio
response_lms = loomcast.chat(
    model="qwen2.5-coder-7b",
    messages=[{"role": "user", "content": "Hello!"}],
    runtime_type="lmstudio",
)

# Obtenir directement l'adaptateur de runtime
manager = loomcast.get_manager()
llamacpp_adapter = manager.get_runtime("llamacpp")

if llamacpp_adapter.is_available():
    print("llama-server est actif sur le port 8080!")
```

### C. Via la Configuration Globale (`default_backend`)
Pour modifier le backend par défaut de manière permanente :

#### En CLI
```bash
loomcast config --set-default lmstudio
```

#### Dans le fichier `config.toml`
```toml
default_backend = "lmstudio"
```

#### Via variable d'environnement (temporaire ou dans la session shell)
```bash
export LOOMCAST_DEFAULT_BACKEND="llamacpp"
```
