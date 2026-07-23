from __future__ import annotations

from typing import Protocol, runtime_checkable

from loomcast.domain.entities import CatalogEntry


@runtime_checkable
class CatalogPort(Protocol):
    """Abstract port for querying model catalog information."""

    def search(self, query: str) -> list[CatalogEntry]:
        """Search the catalog for matching models."""
        ...

    def get_entry(self, name: str) -> CatalogEntry | None:
        """Retrieve catalog details for a model by name."""
        ...
