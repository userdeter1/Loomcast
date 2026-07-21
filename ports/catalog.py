import sys
from typing import List, Optional
from domain.entities import CatalogEntry

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class CatalogPort(Protocol):
    """Abstract port for querying model catalog information."""

    def search(self, query: str) -> List[CatalogEntry]:
        """Search the catalog for matching models."""
        ...

    def get_entry(self, name: str) -> Optional[CatalogEntry]:
        """Retrieve catalog details for a model by name."""
        ...
