# Extending Loomcast: adding a new runtime

Loomcast is built on **Clean Architecture** principles (ports and adapters).
That architecture lets you add a new LLM runtime (vLLM, Text Generation WebUI,
LocalAI, and so on) in a highly modular way, without touching the core
application logic.

---

## 1. The `RuntimePort` protocol

Every interaction with an LLM runtime goes through the `RuntimePort` port
defined in [`loomcast/ports/runtime.py`](../loomcast/ports/runtime.py).

Here is the protocol definition:

```python
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RuntimePort(Protocol):
    """Abstract port definition for local LLM runtime interactions."""

    def is_available(self) -> bool:
        """Check if the local runtime daemon/server is running and reachable."""
        ...

    def is_model_installed(self, model: str) -> bool:
        """Check if a specific model is installed/loaded in this runtime."""
        ...

    def install(self, model: str, progress: Any | None = None) -> None:
        """Install or pull a model into the local runtime."""
        ...

    def chat(self, model: str, messages: list[dict[str, Any]]) -> str:
        """Send a list of messages to a model and return the generated text response."""
        ...

    def list_installed(self) -> list[str]:
        """List all installed/available model names in this runtime."""
        ...

    def remove(self, model: str) -> None:
        """Remove or delete an installed model from the local runtime."""
        ...

    def update(self, model: str, progress: Any | None = None) -> bool:
        """Update an installed model in the local runtime and return True if digest changed."""
        ...
```

---

## 2. Reference example: `LlamaCppRuntime`

The most recent and simplest adapter to model your own on is
[`loomcast/adapters/runtimes/llamacpp.py`](../loomcast/adapters/runtimes/llamacpp.py).

Here is a simplified version illustrating the implementation:

```python
from typing import Any

import httpx

from loomcast.common.exceptions import RuntimeExecutionError, RuntimeUnavailableError
from loomcast.ports.runtime import RuntimePort


class CustomRuntime(RuntimePort):
    def __init__(self, base_url: str = "http://localhost:5000", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/health", timeout=2.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def list_installed(self) -> list[str]:
        if not self.is_available():
            raise RuntimeUnavailableError("custom", self.base_url)
        # Query the runtime API
        ...

    def is_model_installed(self, model: str) -> bool:
        return model in self.list_installed()

    def install(self, model: str, progress: Any | None = None) -> None:
        # Download the model, or validate that it is present
        ...

    def chat(self, model: str, messages: list[dict[str, Any]]) -> str:
        # Send the generation request
        ...

    def remove(self, model: str) -> None:
        # Delete the model, or raise an explanatory error if the runtime
        # exposes no deletion endpoint
        ...

    def update(self, model: str, progress: Any | None = None) -> bool:
        # Re-pull the model and report whether its digest changed
        ...
```

---

## 3. Steps to integrate a fourth runtime

To add a new runtime (for example `vllm`), follow these steps:

### Step 1: declare the type in the domain
Add the enum value in `loomcast/domain/entities.py`:

```python
class RuntimeType(str, Enum):
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    LLAMACPP = "llamacpp"
    VLLM = "vllm"  # New runtime
```

### Step 2: add the configuration URL
Add the setting and its environment mapping in `loomcast/common/config.py`:

```python
class LoomcastConfig(BaseModel):
    # ...
    vllm_url: str = Field(default="http://localhost:8000")
```

### Step 3: create the adapter
Create `loomcast/adapters/runtimes/vllm.py`, implementing `RuntimePort`.

### Step 4: register the adapter in `LoomcastManager`
Update the `self.runtimes` dictionary in `loomcast/core/manager.py`:

```python
self.runtimes = {
    RuntimeType.OLLAMA: OllamaRuntime(base_url=self.config.ollama_url),
    RuntimeType.LMSTUDIO: LMStudioRuntime(base_url=self.config.lmstudio_url),
    RuntimeType.LLAMACPP: LlamaCppRuntime(base_url=self.config.llamacpp_url),
    RuntimeType.VLLM: VllmRuntime(base_url=self.config.vllm_url),
}
```

---

## 4. The strict Clean Architecture rule

> [!IMPORTANT]
> **Separation of concerns**: **never** make the `domain/` or `ports/` layer
> depend on a third-party network or I/O library (`httpx`, `requests`,
> `aiohttp`, and so on).

- The **domain** layer (`loomcast/domain/`) contains pure entities only
  (dataclasses / Pydantic models).
- The **ports** layer (`loomcast/ports/`) contains interfaces and type protocols
  only.
- All network logic and HTTP calls must live exclusively in the **adapters**
  layer (`loomcast/adapters/runtimes/`).
