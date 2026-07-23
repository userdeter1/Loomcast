from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CachePort(Protocol):
    """Abstract port for content-addressed cache storage."""

    def get(self, key: str) -> bytes | None:
        """Retrieve cached bytes by key."""
        ...

    def put(self, key: str, value: bytes) -> None:
        """Store bytes into cache under key."""
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...
