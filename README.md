<p align="center">
  <img src="logo.svg" alt="Loomcast Logo" width="160" height="160" />
</p>

# Loomcast

<p align="center">
  <strong font-size="20">Unified Python SDK & CLI for Local LLM Runtimes</strong>
  <br />
  <em>Orchestrate Ollama, LM Studio, and llama.cpp behind one clean interface.</em>
</p>

<p align="center">
  <a href="https://github.com/userdeter1/Loomcast/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/userdeter1/Loomcast/ci.yml?branch=main&label=CI&style=flat-square" alt="CI Status" /></a>
  <a href="https://github.com/userdeter1/Loomcast/actions/workflows/ci.yml"><img src="https://img.shields.io/badge/coverage-82%25-brightgreen.svg?style=flat-square" alt="Coverage" /></a>
  <a href="https://pypi.org/project/loomcast/"><img src="https://img.shields.io/pypi/v/loomcast.svg?style=flat-square&color=blue" alt="PyPI Package" /></a>
  <a href="https://www.python.org"><img src="https://img.shields.io/badge/python-3.9%2B-blue.svg?style=flat-square" alt="Python Version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License: MIT" /></a>
</p>

---

## Overview

**Loomcast** is a developer-first Python SDK and CLI tool designed to seamlessly manage, discover, compare, and query local Large Language Model (LLM) runtimes.

Whether you run **Ollama**, **LM Studio**, or **llama.cpp**, Loomcast wraps their disparate REST APIs behind a single, resilient, hexagonal interface — so you never have to remember different ports, routes, or payload schemas again.

---

## Key Features

- **Unified Inference API**: Query any model on any local runtime using a single function call: `loomcast.chat()` or `loomcast chat`.
- **Side-by-Side Multi-Runtime Benchmarking**: Send one prompt simultaneously to every active runtime with `loomcast compare` and read responses in parallel panels.
- **5-Level Automated System Doctor**: Run `loomcast doctor` to audit configuration files, `LOOMCAST_*` environment variables, HTTP connectivity, catalog reachability, and cryptographic SHA-256 checksums.
- **Smart Model Catalog & Task Recommendations**: Search models by keyword or get task-tailored recommendations (`coding`, `reasoning`, `math`, `vision`).
- **Batch Category Installer**: Download entire model categories in parallel (`loomcast install-category code`) with configurable concurrency.
- **Cryptographic SHA-256 Verification**: Verify model integrity against SHA-256 manifests to ensure local weight files are not corrupted.
- **Offline Resilient Architecture**: Automatically falls back to an embedded checksum-verified static catalog whenever network access is unavailable.

---

## Installation

Install Loomcast from PyPI:

```bash
pip install loomcast
```

To install from source in editable mode with development dependencies:

```bash
git clone https://github.com/userdeter1/Loomcast.git
cd Loomcast
pip install -e ".[dev]"
```

---

## Architecture Overview

Loomcast uses a **Hexagonal Ports and Adapters** architecture. The core domain logic is decoupled from network details:

```
                      +-------------------+
                      |   Loomcast CLI    |
                      +---------+---------+
                                |
                                v
+-------------------+ +-------------------+ +-------------------+
|  Python SDK Apps  |->|  LoomcastManager  |<-|  Dynamic Catalog  |
+-------------------+ +---------+---------+ +-------------------+
                                |
                     +----------+----------+
                     |   RuntimePort (API) |
                     +----+-----+-----+----+
                          |     |     |
            +-------------+     |     +-------------+
            v                   v                   v
     +--------------+    +--------------+    +--------------+
     | OllamaPort   |    | LMStudioPort |    | LlamaCppPort |
     | (:11434)     |    | (:1234)      |    | (:8080)      |
     +--------------+    +--------------+    +--------------+
```

---

## Quick Start

### 1. Command Line Interface (CLI)

```bash
# Check status and endpoints of all local runtimes
loomcast status

# Run automated system diagnostics
loomcast doctor

# Compare one prompt across all active runtimes side by side
loomcast compare "Explain recursion in one sentence."

# Search the model catalog for coding assistants
loomcast search code

# Recommend models for specific tasks
loomcast recommend coding

# Install a model (Ollama)
loomcast install llama3 --backend ollama

# Batch install all models in a category with 3 concurrent downloads
loomcast install-category code --backend ollama --max-concurrent 3

# Send a prompt to a model
loomcast chat llama3 "Hello world!" --backend ollama

# Verify cryptographic SHA-256 integrity
loomcast verify llama3 --backend ollama

# Update an installed model
loomcast update llama3 --backend ollama

# Remove an installed model
loomcast remove llama3 --backend ollama --yes

# View or update global configuration
loomcast config --set-default lmstudio
```

#### Terminal Preview: `loomcast compare`

```text
$ loomcast compare "Explain recursion in one sentence."

┌── OLLAMA (llama3) ────────┐ ┌── LMSTUDIO (qwen) ────────┐ ┌── LLAMACPP (gemma) ───────┐
│ Recursion is a process    │ │ When a function calls     │ │ A function that calls     │
│ where a function calls    │ │ itself repeatedly until   │ │ itself until reaching a   │
│ itself until a base case. │ │ reaching a base condition.│ │ base termination step.    │
└───────────────────────────┘ └───────────────────────────┘ └────────────────────────────┘
```

---

### 2. Python SDK

```python
import loomcast

# 1. Search the catalog
for entry in loomcast.search("code"):
    print(entry.name, "-", entry.description)

# 2. Get task recommendations
recs = loomcast.recommend("coding")

# 3. List installed models across runtimes
installed = loomcast.list_installed(runtime_type="ollama")

# 4. Single-endpoint chat query
response = loomcast.chat(
    model="llama3",
    messages=[{"role": "user", "content": "Explain recursion in one sentence."}],
    runtime_type="ollama",
)
print("Response:", response)

# 5. Side-by-side multi-runtime comparison
results = loomcast.compare("Explain recursion in one sentence.")
for r in results:
    print(f"{r.runtime_type.value.upper()} -> {r.response or r.error}")

# 6. Verify model SHA-256 integrity
verification = loomcast.verify("llama3", runtime_type="ollama")
print(f"Verified: {verification.verified}, Digest: {verification.digest}")
```

#### Advanced SDK Usage: Dependency Injection

```python
from loomcast import LoomcastConfig, LoomcastManager, RuntimeType

config = LoomcastConfig(
    default_backend=RuntimeType.OLLAMA,
    ollama_url="http://127.0.0.1:11434",
    timeout=60.0,
)

manager = LoomcastManager(config=config)
print(manager.list_available_runtimes())
```

---

## Command Reference Matrix

| Command | CLI Syntax | Python SDK Equivalent | Description |
| :--- | :--- | :--- | :--- |
| `status` | `loomcast status` | `manager.list_available_runtimes()` | Live runtime connectivity check |
| `doctor` | `loomcast doctor` | `StaticCatalog()`, `LoomcastConfig` | 5-level system & health diagnostic |
| `list` | `loomcast list [-b backend]` | `loomcast.list_installed()` | List locally installed models |
| `install` | `loomcast install <model>` | `loomcast.install()` | Download model via runtime API |
| `update` | `loomcast update <model>` | `loomcast.update()` | Verify digest and update model |
| `verify` | `loomcast verify <model>` | `loomcast.verify()` | Check SHA-256 local file integrity |
| `remove` | `loomcast remove <model>` | `loomcast.remove()` | Delete local model weights |
| `search` | `loomcast search <query>` | `loomcast.search()` | Query catalog index |
| `recommend`| `loomcast recommend <task>`| `loomcast.recommend()` | Recommend models by task tag |
| `install-category`| `loomcast install-category <cat>`| `loomcast.install_category()` | Batch parallel category installer |
| `chat` | `loomcast chat <model> <prompt>`| `loomcast.chat()` | Unified single-model inference |
| `compare` | `loomcast compare <prompt>` | `loomcast.compare()` | Multi-runtime parallel benchmark |
| `config` | `loomcast config [--set-default]`| `LoomcastConfig.load()` | View or update persistent config |

---

## Supported Runtimes Matrix

| Feature / Operation | Ollama | LM Studio | llama.cpp |
| :--- | :---: | :---: | :---: |
| **Default Port** | `11434` | `1234` | `8080` |
| **Status / Ping** | Yes | Yes | Yes |
| **Chat Inference** | Yes | Yes | Yes |
| **Model Comparison** | Yes | Yes | Yes |
| **List Installed Models** | Yes | Yes | Yes |
| **Dynamic API Install** | Yes | Manual via UI | Manual via CLI |
| **Digest Integrity Verify** | Yes | N/A | N/A |

---

## Documentation Guides

Explore detailed guides in the [`docs/`](docs/) directory:

- [Getting Started](docs/getting-started.md) — Installation, quick setup, and first chat.
- [Configuration Guide](docs/configuration.md) — Environment variables and `config.json` options.
- [Supported Runtimes](docs/runtimes.md) — Setup details for Ollama, LM Studio, and llama.cpp.
- [CLI Reference](docs/cli-reference.md) — Complete command-line manual.
- [Python SDK Reference](docs/python-sdk-reference.md) — Complete Python API reference & exceptions.
- [Extending & Architecture](docs/extending.md) — Hexagonal architecture & custom runtime adapters.
- [Troubleshooting & FAQ](docs/troubleshooting.md) — Diagnostics, network troubleshooting, and FAQ.

---

## Development & Testing

Loomcast maintains high test coverage and strict linting standards.

### Running Tests

```bash
# Run unit & integration tests
pytest

# Run tests with coverage report
pytest --cov=loomcast --cov-report=term-missing
```

### Code Formatting & Linting

```bash
# Run Ruff linter and formatter
ruff check .
ruff format .
```

---

## License

Loomcast is released under the [MIT License](LICENSE).
