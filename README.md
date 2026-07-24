# Loomcast

[![CI Status](https://img.shields.io/github/actions/workflow/status/userdeter1/Loomcast/ci.yml?branch=main&label=CI)](https://github.com/userdeter1/Loomcast/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen.svg)](https://github.com/userdeter1/Loomcast/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)

Python SDK and CLI for seamlessly managing local LLM runtimes (**Ollama**, **LM Studio**, and **llama.cpp**).

## Installation

```bash
pip install loomcast
```

To work on Loomcast itself, install it from a clone in editable mode with the
development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

```bash
# Check status of local runtimes
loomcast status

# Diagnose configuration, runtimes, catalog and integrity
loomcast doctor

# List installed models
loomcast list

# Search catalog for models
loomcast search code

# Recommend models for a specific task or tag
loomcast recommend coding

# Install a model
loomcast install llama3 --backend ollama

# Batch install all models in a category
loomcast install-category code --backend ollama

# Send a prompt to a model
loomcast chat llama3 "Hello world!" --backend ollama

# Verify installed model integrity
loomcast verify llama3 --backend ollama

# Update an installed model
loomcast update llama3 --backend ollama

# Remove an installed model
loomcast remove llama3 --backend ollama

# View or change configuration
loomcast config
loomcast config --set-default lmstudio
```

Model installation, removal and updating are driven through the runtime's API,
which only Ollama exposes. LM Studio and llama.cpp report an explanatory error
instead: load models through the LM Studio application, or start `llama-server`
with the model you want.

### Python SDK Usage

```python
import loomcast

print(loomcast.__version__)

# Search catalog
results = loomcast.search("code")
for model in results:
    print(model.name, model.description)

# Recommend models for a task
recs = loomcast.recommend("coding")

# List what is installed locally
print(loomcast.list_installed())

# Install a model, and batch install a whole category
loomcast.install("llama3", runtime_type="ollama")
installed, failed = loomcast.install_category("code", runtime_type="ollama")

# Send chat messages
response = loomcast.chat(
    "llama3", [{"role": "user", "content": "Hello!"}], runtime_type="ollama"
)
print(response)

# Verify model integrity
verification = loomcast.verify("llama3", runtime_type="ollama")
print(f"Verified: {verification.verified}, Digest: {verification.digest}")

# Update returns True when the digest changed, False when already current
changed = loomcast.update("llama3", runtime_type="ollama")

# Remove an installed model
loomcast.remove("llama3", runtime_type="ollama")
```

For finer control over configuration or dependency injection, drive
`LoomcastManager` directly:

```python
from loomcast import LoomcastConfig, LoomcastManager

manager = LoomcastManager(config=LoomcastConfig(default_backend="ollama"))
print(manager.list_available_runtimes())
```

## Documentation

Detailed documentation guides are available in the [`docs/`](docs/) directory:

- [Getting started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Supported runtimes](docs/runtimes.md)
- [Extending & architecture](docs/extending.md)
- [CLI reference](docs/cli-reference.md)
