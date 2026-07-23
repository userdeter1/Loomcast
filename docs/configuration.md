# Configuring Loomcast

Loomcast uses a flexible configuration system built on a cross-platform TOML
file with environment variable support.

---

## 1. Configuration file location

The path to `config.toml` is resolved dynamically by the `platformdirs` library,
based on your operating system:

| Operating system | Standard `config.toml` path |
| :--- | :--- |
| **Linux** | `~/.config/loomcast/config.toml` (or `$XDG_CONFIG_HOME/loomcast/config.toml`) |
| **macOS** | `~/Library/Application Support/loomcast/config.toml` |
| **Windows** | `%APPDATA%\loomcast\config.toml` (e.g. `C:\Users\<Name>\AppData\Roaming\loomcast\config.toml`) |

If the file does not exist the first time Loomcast runs, a `config.toml`
containing the default values is generated automatically at that location.

---

## 2. `LoomcastConfig` fields

Here is the full structure of the TOML file, with a description of each setting:

```toml
# config.toml
default_backend = "ollama"
ollama_url = "http://localhost:11434"
lmstudio_url = "http://localhost:1234"
llamacpp_url = "http://localhost:8080"
catalog_source = "https://ollama.com/library"
```

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `default_backend` | `str` / `Enum` | `"ollama"` | Runtime backend used by default when no `--backend` is given on the CLI or in the SDK (`ollama`, `lmstudio`, `llamacpp`). |
| `ollama_url` | `str` | `"http://localhost:11434"` | Base URL of the local or remote Ollama server API. |
| `lmstudio_url` | `str` | `"http://localhost:1234"` | Base URL of the LM Studio OpenAI-compatible server API. |
| `llamacpp_url` | `str` | `"http://localhost:8080"` | Base URL of the `llama-server` (llama.cpp) API. |
| `catalog_source` | `str` | `"https://ollama.com/library"` | Index source for the dynamic model catalog. |

---

## 3. Environment variables

Every configuration field can be overridden through its matching environment
variable:

| Environment variable | Target field | Example value |
| :--- | :--- | :--- |
| `LOOMCAST_DEFAULT_BACKEND` | `default_backend` | `lmstudio` |
| `LOOMCAST_OLLAMA_URL` | `ollama_url` | `http://192.168.1.50:11434` |
| `LOOMCAST_LMSTUDIO_URL` | `lmstudio_url` | `http://localhost:5000` |
| `LOOMCAST_LLAMACPP_URL` | `llamacpp_url` | `http://localhost:8081` |
| `LOOMCAST_CATALOG_SOURCE` | `catalog_source` | `https://custom-catalog.internal/api` |

---

## 4. Configuration precedence

When loading configuration (`LoomcastConfig.load()`), Loomcast applies this
hierarchy strictly:

```
[ LOOMCAST_* environment variables ]  (highest priority)
                  ↓
        [ config.toml file ]
                  ↓
      [ model default values ]        (lowest priority)
```

1. **Environment variables (`LOOMCAST_*`)**: override everything else.
2. **`config.toml` file**: used when the environment variable is not set.
3. **Code defaults (`LoomcastConfig`)**: used when the config file does not
   specify a field.

---

## 5. Worked example: temporary override without editing the file

You can temporarily override a server URL or the default backend for a single
CLI command, without touching your persistent `config.toml`.

### On Linux / macOS (Bash / Zsh)
```bash
# Temporarily point Ollama at a remote machine
LOOMCAST_OLLAMA_URL="http://192.168.1.100:11434" loomcast status

# Run a chat session, temporarily forcing LM Studio as the default backend
LOOMCAST_DEFAULT_BACKEND="lmstudio" loomcast chat qwen2.5:0.5b "Hello"
```

### On Windows (PowerShell)
```powershell
# Temporarily set the URL of a remote llama.cpp server
$env:LOOMCAST_LLAMACPP_URL = "http://192.168.1.100:8080"
loomcast status

# Remove the temporary override
Remove-Item Env:\LOOMCAST_LLAMACPP_URL
```

### From the Python SDK
```python
import os
import loomcast

# Override through an environment variable before initialisation
os.environ["LOOMCAST_OLLAMA_URL"] = "http://192.168.1.100:11434"

# The manager picks the environment variable up automatically
manager = loomcast.get_manager(refresh=True)
print(manager.config.ollama_url)  # http://192.168.1.100:11434
```
