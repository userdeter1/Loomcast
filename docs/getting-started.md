# Getting started with Loomcast

This guide walks you through installing and getting started with **Loomcast**, a
manager and orchestration layer for local LLM runtimes (**Ollama**, **LM Studio**
and **llama.cpp**).

---

## 1. Installation

### Standard user install
To install Loomcast into your Python environment:

```bash
pip install .
```

### Development install
If you want to contribute to the project or modify the source:

```bash
pip install -e ".[dev]"
```

This installs the Loomcast package in editable mode with the development
dependencies (`pytest`, `ruff`, `httpx`, `tomli-w`, and so on).

---

## 2. Prerequisite: start a local runtime

Before running chat requests or interacting with models, **at least one local LLM
server** must be running and reachable on your machine.

Loomcast supports the following three runtimes, with their default ports:

- **Ollama**: `http://localhost:11434` (start the Ollama app, or `ollama serve`).
- **LM Studio**: `http://localhost:1234` (start the LM Studio app and enable the
  OpenAI-compatible server).
- **llama.cpp** (`llama-server`): `http://localhost:8080` (run
  `llama-server -m /path/to/model.gguf`).

---

## 3. Your first chat from the CLI

Once the local server is ready, you can interact with it straight from your
terminal using `loomcast chat`.

### CLI syntax
```bash
loomcast chat <MODEL> <PROMPT> [--backend <BACKEND>]
```

> **Note**: the first argument is the **model name**, the second is your
> **prompt**.

### CLI examples

Query a model on the default backend (Ollama):
```bash
loomcast chat qwen2.5:0.5b "Hello, introduce yourself briefly."
```

Target the LM Studio backend explicitly:
```bash
loomcast chat qwen2.5-coder-7b-instruct "Write a Python function that computes the Fibonacci sequence." --backend lmstudio
```

---

## 4. Your first chat with the Python SDK

You can also integrate Loomcast into your Python scripts through its SDK.

### Complete, tested example

```python
import loomcast

# 1. Search the catalog for compatible models
results = loomcast.search("qwen")
print(f"Models found in the catalog: {len(results)}")
for entry in results[:3]:
    print(f"- {entry.name}: {entry.description}")

# 2. Check which models are installed on the default backend (Ollama)
installed_models = loomcast.list_installed()
print(f"Locally installed models: {installed_models}")

# 3. Send a chat prompt through the SDK
messages = [
    {"role": "system", "content": "Answer briefly."},
    {"role": "user", "content": "What is the capital of France?"},
]

# Call the SDK chat function
response = loomcast.chat(
    model="qwen2.5:0.5b",
    messages=messages,
    runtime_type="ollama",  # Optional: 'ollama', 'lmstudio', or 'llamacpp'
)

print("\n--- Model response ---")
print(response)
```

### Explicit usage with `LoomcastManager`

For finer control over configuration or dependency injection:

```python
from loomcast import LoomcastConfig, LoomcastManager

# Load a custom configuration
config = LoomcastConfig(default_backend="ollama", ollama_url="http://localhost:11434")
manager = LoomcastManager(config=config)

# Check the status of every local runtime
status = manager.list_available_runtimes()
for runtime, is_online in status.items():
    print(f"Runtime {runtime.value}: {'Online' if is_online else 'Offline'}")

# Run a chat request
response = manager.chat(
    model="qwen2.5:0.5b",
    messages=[{"role": "user", "content": "Explain what an LLM is in two sentences."}],
)
print(response)
```
