import json
from pathlib import Path
from typing import List, Optional, Union
from pydantic import ValidationError

from loomcast.common.exceptions import LoomcastError
from loomcast.domain.entities import CatalogEntry
from loomcast.ports.catalog import CatalogPort


class StaticCatalog(CatalogPort):
    """CatalogPort implementation loading entries from an embedded JSON file."""

    def __init__(self, catalog_path: Optional[Union[str, Path]] = None):
        if catalog_path is None:
            self.catalog_path = Path(__file__).parent / "data" / "catalog.json"
        else:
            self.catalog_path = Path(catalog_path)

        self._entries: List[CatalogEntry] = self._load_catalog()

    def _load_catalog(self) -> List[CatalogEntry]:
        if not self.catalog_path.is_file():
            raise LoomcastError(f"Catalog file not found at '{self.catalog_path}'.")

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise LoomcastError(f"Failed to read catalog JSON file '{self.catalog_path}': {e}") from e

        if not isinstance(data, list):
            raise LoomcastError(f"Catalog JSON file '{self.catalog_path}' must contain a list of entries.")

        entries: List[CatalogEntry] = []
        for idx, item in enumerate(data):
            try:
                entry = CatalogEntry.model_validate(item)
                entries.append(entry)
            except ValidationError as ve:
                raise LoomcastError(
                    f"Invalid CatalogEntry format at index {idx} in '{self.catalog_path}': {ve}"
                ) from ve

        return entries

    def search(self, query: str) -> List[CatalogEntry]:
        """Search catalog entries matching query in name, description, or tags (case-insensitive)."""
        query_lower = query.lower()
        results: List[CatalogEntry] = []

        for entry in self._entries:
            name_match = query_lower in entry.name.lower()
            desc_match = bool(entry.description and query_lower in entry.description.lower())
            tag_match = any(query_lower in tag.lower() for tag in entry.tags)

            if name_match or desc_match or tag_match:
                results.append(entry)

        return results

    def get_entry(self, name: str) -> Optional[CatalogEntry]:
        """Retrieve exact catalog entry by name (case-insensitive comparison)."""
        name_lower = name.lower()
        for entry in self._entries:
            if entry.name.lower() == name_lower:
                return entry
        return None
