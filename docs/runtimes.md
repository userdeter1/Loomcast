# Supported runtimes and backend management

Loomcast provides an abstraction layer that lets you drive several local LLM
runtime servers through a single, unified interface.

---

## 1. Runtime comparison

| Capability | Ollama | LM Studio | llama.cpp (`llama-server`) |
| :--- | :--- | :--- | :--- |
| **Backend enum** | `ollama` | `lmstudio` | `llamacpp` |
| **Default port** | `11434` | `1234` | `8080` |
| **API protocol** | Native REST API (`/api/chat`, `/api/pull`, `/api/tags`) | OpenAI-compatible API (`/v1/chat/completions`, `/v1/models`) | OpenAI-compatible API (`/v1/chat/completions`, `/v1/models`, `/health`) |
| **Model installation** | **Automatic** through the API (`POST /api/pull`) | **Manual**, inside the LM Studio application | **Manual**, at server startup (`llama-server -m`) |
| **Integrity verification** | **Available** (SHA-256 digest returned by the Ollama API) | **Unavailable** (`/v1/models` exposes no digests) | **Unavailable** (the REST API provides no digests) |
| **Concurrent models** | Several models managed per instance | Depends on what the application is configured for | **One model** loaded at a time per `llama-server` instance |

---

## 2. Known limitations per runtime

### Ollama (`ollama`)
- **Strengths**: native support for model downloads with real-time progress
  reporting, and full integrity verification through the SHA-256 digest
  (`loomcast verify`).

### LM Studio (`lmstudio`)
- **Installation**: LM Studio exposes no public HTTP endpoint for downloading
  models remotely through an API. Models must be searched for and loaded
  beforehand in the LM Studio GUI.
- **Verification**: `loomcast verify` reports an unverified status, because the
  LM Studio OpenAI-compatible API includes no cryptographic signatures.

### llama.cpp (`llamacpp`)
- **Single model**: a `llama-server` instance serves **exactly one model**,
  chosen when the executable starts (`-m /path/to/model.gguf`).
- **API installation**: there is no hot download through the REST API. Trying to
  install a model that is not loaded returns an error message telling you to
  restart the server with the model you want.

---

## 3. Switching between runtimes

Loomcast lets you switch backends through three distinct mechanisms.

### A. With the CLI flag (`--backend` / `-b`)
To override the runtime for a single CLI command:

```bash
# Check which models are loaded in LM Studio
loomcast list --backend lmstudio

# Download a model into Ollama
loomcast install qwen2.5:0.5b -b ollama

# Chat with a model served by llama-server
loomcast chat gemma-2-2b "Explain the principles of Clean Architecture." --backend llamacpp
```

### B. From the Python SDK (`runtime_type`)
In your Python scripts, pass the `runtime_type` parameter:

```python
import loomcast

# Request against LM Studio
response_lms = loomcast.chat(
    model="qwen2.5-coder-7b",
    messages=[{"role": "user", "content": "Hello!"}],
    runtime_type="lmstudio",
)

# Get the runtime adapter directly
manager = loomcast.get_manager()
llamacpp_adapter = manager.get_runtime("llamacpp")

if llamacpp_adapter.is_available():
    print("llama-server is running on port 8080!")
```

### C. Through global configuration (`default_backend`)
To change the default backend permanently:

#### From the CLI
```bash
loomcast config --set-default lmstudio
```

#### In `config.toml`
```toml
default_backend = "lmstudio"
```

#### Through an environment variable (temporary, or for the shell session)
```bash
export LOOMCAST_DEFAULT_BACKEND="llamacpp"
```
