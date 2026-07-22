# Prise en main de Loomcast

Ce guide vous accompagne pour installer et commencer à utiliser **Loomcast**, un gestionnaire d'apprentissage et d'orchestration pour rênes d'exécution de LLMs locaux (**Ollama**, **LM Studio** et **llama.cpp**).

---

## 1. Installation

### En mode utilisateur standard
Pour installer Loomcast dans votre environnement Python :

```bash
pip install .
```

### En mode développement
Si vous souhaitez contribuer au projet ou modifier le code source :

```bash
pip install -e ".[dev]"
```

Cette commande installe le package Loomcast en mode éditable avec les dépendances de développement (`pytest`, `ruff`, `httpx`, `tomli-w`, etc.).

---

## 2. Prérequis : Démarrer un Runtime Local

Avant d'exécuter des requêtes de chat ou d'interagir avec les modèles, **au moins un serveur LLM local** doit être lancé et accessible sur votre machine.

Loomcast supporte les trois runtimes suivants avec leurs ports par défaut :

- **Ollama** : `http://localhost:11434` (Lancez l'application Ollama ou `ollama serve`).
- **LM Studio** : `http://localhost:1234` (Lancez l'application LM Studio et activez le serveur OpenAI-compatible).
- **llama.cpp** (`llama-server`) : `http://localhost:8080` (Exécutez `llama-server -m /chemin/vers/modèle.gguf`).

---

## 3. Premier Chat en CLI

Une fois le serveur local prêt, vous pouvez interagir directement depuis votre terminal avec la commande `loomcast chat`.

### Syntaxe CLI
```bash
loomcast chat <MODELE> <PROMPT> [--backend <BACKEND>]
```

> **Remarque** : Le premier argument est le **nom du modèle**, et le second est votre **prompt**.

### Exemples CLI

Interroger un modèle sur le backend par défaut (Ollama) :
```bash
loomcast chat qwen2.5:0.5b "Bonjour, présente-toi brièvement."
```

Spécifier explicitement le backend LM Studio :
```bash
loomcast chat qwen2.5-coder-7b-instruct "Écris une fonction Python qui calcule la suite de Fibonacci." --backend lmstudio
```

---

## 4. Premier Chat avec le SDK Python

Vous pouvez également intégrer Loomcast dans vos scripts Python via son SDK.

### Exemple complet et testé

```python
import loomcast

# 1. Rechercher des modèles compatibles dans le catalogue
results = loomcast.search("qwen")
print(f"Modèles trouvés dans le catalogue : {len(results)}")
for entry in results[:3]:
    print(f"- {entry.name}: {entry.description}")

# 2. Vérifier les modèles installés sur le backend par défaut (Ollama)
installed_models = loomcast.list_installed()
print(f"Modèles installés en local : {installed_models}")

# 3. Envoyer un prompt de chat via le SDK
messages = [
    {"role": "system", "content": "Tu me réponds brièvement."},
    {"role": "user", "content": "Quelle est la capitale de la France ?"}
]

# Appel de la fonction chat du SDK
response = loomcast.chat(
    model="qwen2.5:0.5b",
    messages=messages,
    runtime_type="ollama"  # Optionnel: 'ollama', 'lmstudio', ou 'llamacpp'
)

print("\n--- Réponse du modèle ---")
print(response)
```

### Utilisation explicite avec `LoomcastManager`

Pour un contrôle plus fin sur la configuration ou l'injection de dépendances :

```python
from loomcast import LoomcastConfig, LoomcastManager

# Charger la configuration personnalisée
config = LoomcastConfig(default_backend="ollama", ollama_url="http://localhost:11434")
manager = LoomcastManager(config=config)

# Vérifier le statut de tous les runtimes locaux
status = manager.list_available_runtimes()
for runtime, is_online in status.items():
    print(f"Runtime {runtime.value}: {'En ligne' if is_online else 'Hors ligne'}")

# Exécuter une requête de chat
response = manager.chat(
    model="qwen2.5:0.5b",
    messages=[{"role": "user", "content": "Explique ce qu'est un LLM en 2 phrases."}]
)
print(response)
```
