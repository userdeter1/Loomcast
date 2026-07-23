# Loomcast

[![CI Status](https://img.shields.io/github/actions/workflow/status/userdeter1/Loomcast/ci.yml?branch=main&label=CI)](https://github.com/userdeter1/Loomcast/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen.svg)](https://github.com/userdeter1/Loomcast/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)

Python SDK and CLI for seamlessly managing local LLM runtimes (**Ollama**, **LM Studio**, and **llama.cpp**).

## Installation

```bash
pip install -e .
```

## Quick Start

### CLI Usage

```bash
# Check status of local runtimes
loomcast status

# List installed models
loomcast list

# Search catalog for models
loomcast search code

# Recommend models for a specific task or tag
loomcast recommend coding

# Batch install all models in a category
loomcast install-category code --backend ollama

# Send a prompt to a model
loomcast chat llama3 "Hello world!" --backend ollama

# Verify installed model integrity
loomcast verify llama3 --backend ollama
```

### Python SDK Usage

```python
import loomcast

# Initialize manager
manager = loomcast.LoomcastManager()

# Search catalog
results = loomcast.search("code")
for model in results:
    print(model.name, model.description)

# Recommend models for a task
recs = loomcast.recommend("coding")

# Batch install category
installed, failed = loomcast.install_category("code", runtime_type="ollama")

# Send chat messages
response = loomcast.chat(
    "llama3", [{"role": "user", "content": "Hello!"}], runtime_type="ollama"
)
print(response)

# Verify model integrity
verification = loomcast.verify("llama3", runtime_type="ollama")
print(f"Verified: {verification.verified}, Digest: {verification.digest}")
```

## Documentation

Detailed documentation guides are available in the [`docs/`](docs/) directory:

- [Prise en main (Getting Started)](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Runtimes Supportés](docs/runtimes.md)
- [Extension & Architecture](docs/extending.md)
- [Référence CLI](docs/cli-reference.md)
