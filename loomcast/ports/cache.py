import sys
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class CachePort(Protocol):
    """Abstract port for content-addressed cache storage."""

    def get(self, key: str) -> Optional[bytes]:
        """Retrieve cached bytes by key."""
        ...

    def put(self, key: str, value: bytes) -> None:
        """Store bytes into cache under key."""
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...
