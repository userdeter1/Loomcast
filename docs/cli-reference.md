# Loomcast CLI reference

Loomcast ships a command-line interface built with
[Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/).

Every command is available through the `loomcast` executable (or
`python -m loomcast.cli.main`).

---

## Command overview

```bash
loomcast [COMMAND] [ARGS] [OPTIONS]
```

---

## 1. `loomcast status`

Shows the operational state (online / offline), the endpoint URL, and the
default runtime for every configured backend (**Ollama**, **LM Studio**,
**llama.cpp**).

### Syntax
```bash
loomcast status
```

### Sample output
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

Lists every model installed and available across the local runtimes.

### Syntax
```bash
loomcast list [OPTIONS]
```

### Options
- `-b, --backend TEXT`: filter by a specific runtime (`ollama`, `lmstudio`,
  `llamacpp`).

### Examples
```bash
# List models across every runtime
loomcast list

# List Ollama models only
loomcast list --backend ollama
```

---

## 3. `loomcast install`

Downloads and installs a model into the target runtime (for runtimes that
support hot installation through an API, such as Ollama).

### Syntax
```bash
loomcast install MODEL [OPTIONS]
```

### Arguments
- `MODEL` (required): identifier of the model to install (e.g. `qwen2.5:0.5b`,
  `llama3`).

### Options
- `-b, --backend TEXT`: target backend (`ollama`, `lmstudio`, `llamacpp`).
  Defaults to the configured default backend.

### Example
```bash
loomcast install qwen2.5:0.5b --backend ollama
```

---

## 4. `loomcast remove`

Removes an installed model from the target runtime (for example through Ollama's
`DELETE /api/delete` API). Prompts for interactive confirmation before deleting,
unless `--yes` is passed.

### Syntax
```bash
loomcast remove MODEL [OPTIONS]
```

### Arguments
- `MODEL` (required): identifier of the model to remove (e.g. `qwen2.5:0.5b`,
  `llama3`).

### Options
- `-b, --backend TEXT`: target backend (`ollama`, `lmstudio`, `llamacpp`).
  Defaults to the configured default backend.
- `-y, --yes`: skip the interactive confirmation prompt (useful in scripts).

### Examples
```bash
# Interactive removal
loomcast remove qwen2.5:0.5b

# Removal without confirmation, on an explicit backend
loomcast remove llama3 --backend ollama --yes
```

---

## 5. `loomcast update`

Updates a model already installed on the target runtime (for example by
re-pulling on Ollama and comparing the SHA-256 digest). The message differs
depending on whether the model was updated or was already up to date.

### Syntax
```bash
loomcast update MODEL [OPTIONS]
```

### Arguments
- `MODEL` (required): identifier of the model to update (e.g. `qwen2.5:0.5b`,
  `llama3`).

### Options
- `-b, --backend TEXT`: target backend (`ollama`, `lmstudio`, `llamacpp`).
  Defaults to the configured default backend.

### Example
```bash
loomcast update qwen2.5:0.5b --backend ollama
```

---

## 6. `loomcast chat`

Sends a prompt to a local LLM and displays its response in a formatted panel.

### Syntax
```bash
loomcast chat MODEL PROMPT [OPTIONS]
```

> **Careful**: the `MODEL` argument comes **first**, followed by the `PROMPT`
> text.

### Arguments
- `MODEL` (required): name of the loaded model.
- `PROMPT` (required): the question or request text.

### Options
- `-b, --backend TEXT`: target backend (`ollama`, `lmstudio`, `llamacpp`).

### Examples
```bash
# Chat on the default backend
loomcast chat qwen2.5:0.5b "Explain recursion in two sentences."

# Chat with a model on LM Studio
loomcast chat qwen2.5-coder-7b "Write a bash script that lists files." -b lmstudio
```

---

## 7. `loomcast config`

Views or updates Loomcast's persistent configuration (`config.toml`).

### Syntax
```bash
loomcast config [OPTIONS]
```

### Options
- `--set-default TEXT`: set the default backend (`ollama`, `lmstudio`,
  `llamacpp`).
- `--show / --no-show`: show or hide the current configuration table (default:
  `--show`).

### Examples
```bash
# Show the current configuration
loomcast config

# Set LM Studio as the default backend
loomcast config --set-default lmstudio
```

---

## 8. `loomcast search`

Searches for models in the Loomcast index catalog.

### Syntax
```bash
loomcast search QUERY
```

### Arguments
- `QUERY` (required): search keyword (e.g. `code`, `llama`, `vision`).

### Example
```bash
loomcast search code
```

---

## 9. `loomcast recommend`

Finds and recommends models suited to a specific task or tag.

### Syntax
```bash
loomcast recommend TASK
```

### Arguments
- `TASK` (required): task tag or category (e.g. `coding`, `math`,
  `translation`).

### Example
```bash
loomcast recommend coding
```

---

## 10. `loomcast install-category`

Batch-installs every model associated with a given category or tag.

### Syntax
```bash
loomcast install-category CATEGORY [OPTIONS]
```

### Arguments
- `CATEGORY` (required): name of the tag/category to install.

### Options
- `-b, --backend TEXT`: target backend.
- `-c, --max-concurrent INTEGER`: maximum number of parallel downloads
  (default: 3).
- `-s, --sequential`: run the installation sequentially (`max-concurrent=1`).

### Example
```bash
loomcast install-category coding --backend ollama --max-concurrent 2
```

---

## 11. `loomcast verify`

Verifies the cryptographic integrity (SHA-256 digest) of an installed model.

### Syntax
```bash
loomcast verify MODEL [OPTIONS]
```

### Arguments
- `MODEL` (required): name of the model to verify.

### Options
- `-b, --backend TEXT`: backend on which to verify the model.

### Example
```bash
loomcast verify qwen2.5:0.5b --backend ollama
```

---

## 12. `loomcast doctor`

Runs a full diagnostic of the Loomcast environment: TOML configuration,
environment variables, local runtime availability, catalog reachability, and
SHA-256 integrity of the static catalog.

### Syntax
```bash
loomcast doctor
```

### Statuses and exit codes
- `✓ OK`: the check passed.
- `⚠ Warning`: non-blocking issue (e.g. an optional runtime offline, or the
  dynamic catalog falling back to the static one). Exit code `0` if these are
  the only findings.
- `✗ Problem`: blocking issue (e.g. the default backend offline, a
  configuration error, or a tampered static catalog). Exit code `1`.

### Sample output
```
Loomcast System Diagnostics

✓ Configuration: loaded successfully from /home/user/.config/loomcast/config.toml
✓ Environment variables: none set, using defaults
✗ Runtime OLLAMA (default backend): unavailable. Start the service or change the default backend in the config.
⚠ Runtime LMSTUDIO: unavailable (not the default backend)
⚠ Runtime LLAMACPP: unavailable (not the default backend)
✓ Catalog: dynamic catalog reachable
✓ Static catalog integrity: SHA-256 check passed

1 problem(s) found, 2 warning(s)
```
