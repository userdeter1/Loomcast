# Loomcast Python SDK reference

The `loomcast` Python library provides a clean, unified SDK for managing local LLM runtimes (**Ollama**, **LM Studio**, and **llama.cpp**).

---

## 1. Quick Import & High-Level Functions

All major operations are exposed directly at module root level (`import loomcast`):

```python
import loomcast

# 1. Search model catalog
results = loomcast.search("code")

# 2. Get recommendations for a task
recs = loomcast.recommend("coding")

# 3. List installed models
installed = loomcast.list_installed(runtime_type="ollama")

# 4. Check if a model is installed
exists = loomcast.is_model_installed("llama3", runtime_type="ollama")

# 5. Install a single model or batch category
loomcast.install("llama3", runtime_type="ollama")
installed_list, failed_list = loomcast.install_category("code", runtime_type="ollama")

# 6. Send chat prompt
response = loomcast.chat("llama3", [{"role": "user", "content": "Hello!"}], runtime_type="ollama")

# 7. Compare prompt across all active runtimes
results = loomcast.compare("Explain recursion in one sentence.")

# 8. Verify model SHA-256 integrity
res = loomcast.verify("llama3", runtime_type="ollama")

# 9. Update an installed model
changed = loomcast.update("llama3", runtime_type="ollama")

# 10. Remove an installed model
loomcast.remove("llama3", runtime_type="ollama")
```

---

## 2. Top-Level API Reference

### `loomcast.chat(model, messages, runtime_type=None) -> str`
Sends a chat prompt to a local LLM model and returns the response string.
- `model`: (str) Name or identifier of the target model.
- `messages`: (list[dict]) List of message dicts `[{"role": "user"|"system"|"assistant", "content": "..."}]`.
- `runtime_type`: (RuntimeType | str | None) Target backend (`"ollama"`, `"lmstudio"`, `"llamacpp"`). Uses default backend when `None`.

### `loomcast.compare(prompt, runtime_types=None, model=None, models=None, max_concurrent=3) -> list[ComparisonResult]`
Queries multiple runtimes in parallel with the same prompt and returns a list of `ComparisonResult` objects.
- `prompt`: (str) The prompt string sent to each backend.
- `runtime_types`: (list | None) List of target backends (`["ollama", "lmstudio"]`). Queries all active backends when `None`.
- `model`: (str | None) Global model name to use across backends.
- `models`: (dict | None) Dictionary mapping `RuntimeType` to specific model names.
- `max_concurrent`: (int) Maximum parallel queries (default: 3).

### `loomcast.list_installed(runtime_type=None) -> list[str]`
Returns the list of model identifiers installed on the specified backend (or default backend).

### `loomcast.is_model_installed(model, runtime_type=None) -> bool`
Returns `True` if the model is installed on the specified backend.

### `loomcast.install(model, runtime_type=None, progress=None) -> None`
Installs or pulls a model into the target runtime. Accepts a `ProgressReporter` for custom progress callbacks.

### `loomcast.install_category(category, runtime_type=None, max_concurrent=3, progress=None) -> tuple[list[str], list[str]]`
Batch-installs all models tagged with a given category. Returns `(installed_models, failed_models)`.

### `loomcast.update(model, runtime_type=None, progress=None) -> bool`
Checks the model digest against the remote source and updates it if modified. Returns `True` if updated, `False` if already current.

### `loomcast.verify(model, runtime_type=None) -> VerificationResult`
Verifies cryptographic SHA-256 integrity of an installed model. Returns a `VerificationResult` instance.

### `loomcast.remove(model, runtime_type=None) -> None`
Deletes/uninstalls a model from the target runtime.

### `loomcast.search(query) -> list[CatalogEntry]`
Searches the model catalog for matching entries.

### `loomcast.recommend(task) -> list[CatalogEntry]`
Filters recommended models by task tag (`coding`, `reasoning`, `math`, `vision`, etc.).

---

## 3. Core Class: `LoomcastManager`

For dependency injection, custom configuration, or finer control, use `LoomcastManager`:

```python
from loomcast import LoomcastConfig, LoomcastManager, RuntimeType

# Custom configuration
config = LoomcastConfig(
    default_backend=RuntimeType.OLLAMA,
    ollama_url="http://127.0.0.1:11434",
    timeout=60.0,
)

manager = LoomcastManager(config=config)

# Check available runtimes
runtimes_status = manager.list_available_runtimes()
# -> {<RuntimeType.OLLAMA: 'ollama'>: True, <RuntimeType.LMSTUDIO: 'lmstudio'>: False, ...}

# Execute chat through manager
reply = manager.chat("llama3", [{"role": "user", "content": "Hello"}])
```

---

## 4. Domain Entities & Data Classes

```python
from loomcast import CatalogEntry, ComparisonResult, VerificationResult, RuntimeType

# RuntimeType Enum
# RuntimeType.OLLAMA, RuntimeType.LMSTUDIO, RuntimeType.LLAMACPP

# ComparisonResult
# result.runtime_type -> RuntimeType
# result.model        -> str
# result.response     -> str | None
# result.error        -> str | None

# VerificationResult
# res.model        -> str
# res.runtime_type -> RuntimeType
# res.verified     -> bool
# res.digest       -> str | None
# res.message      -> str
```

---

## 5. Exceptions Hierarchy

All Loomcast exceptions inherit from `LoomcastError`:

- `LoomcastError`: Base exception.
- `ConfigurationError`: Failure to parse or load configuration files.
- `RuntimeUnavailableError`: Target runtime HTTP server is offline or unreachable.
- `RuntimeExecutionError`: Error during inference or runtime execution.
- `ModelNotFoundError`: Model not found locally or in catalog.
- `CatalogIntegrityError`: Checksum SHA-256 mismatch in catalog data.
- `CacheError`: Failure reading or writing local cache.

```python
from loomcast import LoomcastError, RuntimeUnavailableError

try:
    response = loomcast.chat("llama3", [{"role": "user", "content": "Hi"}], runtime_type="ollama")
except RuntimeUnavailableError:
    print("Ollama server is not running!")
except LoomcastError as e:
    print("Loomcast error:", e)
```
