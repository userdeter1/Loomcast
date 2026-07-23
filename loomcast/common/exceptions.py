class LoomcastError(Exception):
    """Base exception for all Loomcast errors."""


class RuntimeUnavailableError(LoomcastError):
    """Raised when a local LLM runtime (Ollama, LM Studio) is unreachable."""

    def __init__(self, runtime_name: str, url: str):
        self.runtime_name = runtime_name
        self.url = url
        super().__init__(f"Runtime '{runtime_name}' is unavailable at {url}.")


class ModelNotFoundError(LoomcastError):
    """Raised when a requested model is not installed in the runtime."""

    def __init__(self, model_name: str, runtime_name: str):
        self.model_name = model_name
        self.runtime_name = runtime_name
        super().__init__(
            f"Model '{model_name}' was not found in runtime '{runtime_name}'."
        )


class ConfigurationError(LoomcastError):
    """Raised when configuration loading or saving fails."""


class RuntimeExecutionError(LoomcastError):
    """Raised when a runtime execution or API call fails."""


class CacheError(LoomcastError):
    """Raised when cache operations fail due to I/O or permissions issues."""


class CatalogIntegrityError(LoomcastError):
    """Raised when catalog file integrity verification (SHA-256) fails."""
