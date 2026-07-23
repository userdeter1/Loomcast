# Référence CLI de Loomcast

Loomcast fournit une interface en ligne de commande (CLI) bâtie avec [Typer](https://typer.tiangolo.com/) et [Rich](https://rich.readthedocs.io/).

Toutes les commandes sont accessibles via l'exécutable `loomcast` (ou `python -m loomcast.cli.main`).

---

## Vue d'ensemble des commandes

```bash
loomcast [COMMAND] [ARGS] [OPTIONS]
```

---

## 1. `loomcast status`

Affiche l'état d'opération (en ligne / hors ligne), l'URL d'endpoint et le runtime par défaut pour tous les backends configurés (**Ollama**, **LM Studio**, **llama.cpp**).

### Syntaxe
```bash
loomcast status
```

### Exemple de sortie
```
┌──────────┬────────────────────────┬─────────┬────────┐
│ Runtime  │ Endpoint               │ Default │ Status │
├──────────┼────────────────────────┼─────────┼────────┤
│ OLLAMA   │ http://localhost:11434 │ Yes     │ Online │
│ LMSTUDIO │ http://localhost:1234  │ No      │ Offline│
│ LLAMACPP │ http://localhost:8080  │ No      │ Offline│
└──────────┴────────────────────────┴─────────┴────────┘
```

---

## 2. `loomcast list`

Liste l'ensemble des modèles installés et disponibles sur les runtimes locaux.

### Syntaxe
```bash
loomcast list [OPTIONS]
```

### Options
- `-b, --backend TEXT` : Filtrer par runtime spécifique (`ollama`, `lmstudio`, `llamacpp`).

### Exemples
```bash
# Lister les modèles sur tous les runtimes
loomcast list

# Lister uniquement les modèles Ollama
loomcast list --backend ollama
```

---

## 3. `loomcast install`

Télécharge et installe un modèle dans le runtime cible (pour les runtimes supportant l'installation à chaud via API comme Ollama).

### Syntaxe
```bash
loomcast install MODEL [OPTIONS]
```

### Arguments
- `MODEL` (Requis) : Identifiant du modèle à installer (ex: `qwen2.5:0.5b`, `llama3`).

### Options
- `-b, --backend TEXT` : Backend cible (`ollama` ou `lmstudio`). Si non spécifié, utilise le backend par défaut.

### Exemple
```bash
loomcast install qwen2.5:0.5b --backend ollama
```

---

## 4. `loomcast chat`

Envoie une invite (prompt) à un modèle LLM local et affiche sa réponse dans un panneau mis en forme.

### Syntaxe
```bash
loomcast chat MODEL PROMPT [OPTIONS]
```

> **Attention** : L'argument `MODEL` doit être spécifié en **premier**, suivi du texte du `PROMPT`.

### Arguments
- `MODEL` (Requis) : Le nom du modèle chargé.
- `PROMPT` (Requis) : Le texte de la question / requête.

### Options
- `-b, --backend TEXT` : Backend cible (`ollama`, `lmstudio`, `llamacpp`).

### Exemples
```bash
# Chat avec le backend par défaut
loomcast chat qwen2.5:0.5b "Explique la récursion en 2 phrases."

# Chat avec un modèle sur LM Studio
loomcast chat qwen2.5-coder-7b "Écris un script bash pour lister les fichiers." -b lmstudio
```

---

## 5. `loomcast config`

Consulte ou met à jour la configuration persistance de Loomcast (`config.toml`).

### Syntaxe
```bash
loomcast config [OPTIONS]
```

### Options
- `--set-default TEXT` : Mettre à jour le backend par défaut (`ollama`, `lmstudio`, `llamacpp`).
- `--show / --no-show` : Afficher ou masquer la table de configuration actuelle (par défaut: `--show`).

### Exemples
```bash
# Afficher la configuration actuelle
loomcast config

# Définir LM Studio comme backend par défaut
loomcast config --set-default lmstudio
```

---

## 6. `loomcast search`

Recherche des modèles dans le catalogue d'indexation Loomcast.

### Syntaxe
```bash
loomcast search QUERY
```

### Arguments
- `QUERY` (Requis) : Mot-clé de recherche (ex: `code`, `llama`, `vision`).

### Exemple
```bash
loomcast search code
```

---

## 7. `loomcast recommend`

Recherche et recommande des modèles adaptés à une tâche ou une étiquette (tag) spécifique.

### Syntaxe
```bash
loomcast recommend TASK
```

### Arguments
- `TASK` (Requis) : Étiquette ou catégorie de tâche (ex: `coding`, `math`, `translation`).

### Exemple
```bash
loomcast recommend coding
```

---

## 8. `loomcast install-category`

Installe simultanément en lot tous les modèles associés à une catégorie ou un tag donné.

### Syntaxe
```bash
loomcast install-category CATEGORY [OPTIONS]
```

### Arguments
- `CATEGORY` (Requis) : Nom du tag/catégorie à installer.

### Options
- `-b, --backend TEXT` : Backend cible.
- `-c, --max-concurrent INTEGER` : Nombre maximal de téléchargements parallèles (défaut : 3).
- `-s, --sequential` : Exécuter l'installation de manière séquentielle (`max-concurrent=1`).

### Exemple
```bash
loomcast install-category coding --backend ollama --max-concurrent 2
```

---

## 9. `loomcast verify`

Vérifie l'intégrité cryptographique (digest SHA256) d'un modèle installé.

### Syntaxe
```bash
loomcast verify MODEL [OPTIONS]
```

### Arguments
- `MODEL` (Requis) : Nom du modèle à vérifier.

### Options
- `-b, --backend TEXT` : Backend sur lequel vérifier le modèle.

### Exemple
```bash
loomcast verify qwen2.5:0.5b --backend ollama
```
