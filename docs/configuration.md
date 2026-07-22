# Configuration de Loomcast

Loomcast utilise un système de configuration souple et modulable reposant sur un fichier TOML cross-platform et la prise en charge de variables d'environnement.

---

## 1. Emplacement du Fichier de Configuration

Le chemin du fichier de configuration `config.toml` est déterminé dynamiquement par la bibliothèque `platformdirs` selon le système d'exploitation :

| Système d'exploitation | Chemin standard du fichier `config.toml` |
| :--- | :--- |
| **Linux** | `~/.config/loomcast/config.toml` (ou `$XDG_CONFIG_HOME/loomcast/config.toml`) |
| **macOS** | `~/Library/Application Support/loomcast/config.toml` |
| **Windows** | `%APPDATA%\loomcast\config.toml` (ex. `C:\Users\<Nom>\AppData\Roaming\loomcast\config.toml`) |

Si ce fichier n'existe pas lors du premier lancement de Loomcast, un fichier `config.toml` contenant les valeurs par défaut est automatiquement généré à cet endroit.

---

## 2. Champs du Modèle `LoomcastConfig`

Voici la structure complète du fichier TOML avec la description de chaque paramètre :

```toml
# config.toml
default_backend = "ollama"
ollama_url = "http://localhost:11434"
lmstudio_url = "http://localhost:1234"
llamacpp_url = "http://localhost:8080"
catalog_source = "https://ollama.com/library"
```

| Champ | Type | Valeur par défaut | Description |
| :--- | :--- | :--- | :--- |
| `default_backend` | `str` / `Enum` | `"ollama"` | Runtime backend utilisé par défaut lorsque aucun `--backend` n'est spécifié en CLI ou SDK (`ollama`, `lmstudio`, `llamacpp`). |
| `ollama_url` | `str` | `"http://localhost:11434"` | URL de base de l'API du serveur Ollama local ou distant. |
| `lmstudio_url` | `str` | `"http://localhost:1234"` | URL de base de l'API OpenAI-compatible du serveur LM Studio. |
| `llamacpp_url` | `str` | `"http://localhost:8080"` | URL de base de l'API de `llama-server` (llama.cpp). |
| `catalog_source` | `str` | `"https://ollama.com/library"` | Source d'indexation pour le catalogue de modèles dynamiques. |

---

## 3. Variables d'Environnement

Chaque champ de configuration peut être surchargé à l'aide de sa variable d'environnement correspondante :

| Variable d'environnement | Champ ciblé | Exemple de valeur |
| :--- | :--- | :--- |
| `LOOMCAST_DEFAULT_BACKEND` | `default_backend` | `lmstudio` |
| `LOOMCAST_OLLAMA_URL` | `ollama_url` | `http://192.168.1.50:11434` |
| `LOOMCAST_LMSTUDIO_URL` | `lmstudio_url` | `http://localhost:5000` |
| `LOOMCAST_LLAMACPP_URL` | `llamacpp_url` | `http://localhost:8081` |
| `LOOMCAST_CATALOG_SOURCE` | `catalog_source` | `https://custom-catalog.internal/api` |

---

## 4. Ordre de Priorité des Configurations

Lors du chargement des configurations (`LoomcastConfig.load()`), Loomcast applique strictement la hiérarchie de priorité suivante :

```
[ Variables d'Environnement LOOMCAST_* ]  (Priorité maximale)
                  ↓
       [ Fichier config.toml ]
                  ↓
       [ Valeurs par défaut du Modèle ]  (Priorité minimale)
```

1. **Variables d'environnement (`LOOMCAST_*`)** : Écrasent toutes les autres valeurs.
2. **Fichier `config.toml`** : Utilisé si la variable d'environnement n'est pas définie.
3. **Valeurs par défaut du code (`LoomcastConfig`)** : Utilisées si le fichier de configuration ne spécifie pas un champ.

---

## 5. Exemple Concret : Surcharge Temporaire sans Modifier le Fichier

Vous pouvez surcharger temporairement une URL de serveur ou le backend par défaut pour une seule commande CLI sans altérer votre fichier `config.toml` persistant.

### Sur Linux / macOS (Bash / Zsh)
```bash
# Rediriger temporairement Ollama vers une machine distante
LOOMCAST_OLLAMA_URL="http://192.168.1.100:11434" loomcast status

# Exécuter une session de chat en forçant temporairement LM Studio comme backend par défaut
LOOMCAST_DEFAULT_BACKEND="lmstudio" loomcast chat qwen2.5:0.5b "Hello"
```

### Sur Windows (PowerShell)
```powershell
# Définir temporairement l'URL d'un serveur llama.cpp distant
$env:LOOMCAST_LLAMACPP_URL = "http://192.168.1.100:8080"
loomcast status

# Supprimer la surcharge temporaire
Remove-Item Env:\LOOMCAST_LLAMACPP_URL
```

### En Python SDK
```python
import os
import loomcast

# Surcharge via variable d'environnement avant initialisation
os.environ["LOOMCAST_OLLAMA_URL"] = "http://192.168.1.100:11434"

# Le manager appliquera automatiquement la variable d'environnement
manager = loomcast.get_manager(refresh=True)
print(manager.config.ollama_url)  # http://192.168.1.100:11434
```
