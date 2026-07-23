from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import ValidationError

from loomcast.common.exceptions import CatalogIntegrityError, LoomcastError
from loomcast.domain.entities import CatalogEntry
from loomcast.ports.catalog import CatalogPort


class StaticCatalog(CatalogPort):
    """CatalogPort implementation loading entries from an embedded JSON file."""

    def __init__(self, catalog_path: str | Path | None = None):
        if catalog_path is None:
            self.catalog_path = Path(__file__).parent / "data" / "catalog.json"
        else:
            self.catalog_path = Path(catalog_path)

        self._entries: list[CatalogEntry] = self._load_catalog()

    def _load_catalog(self) -> list[CatalogEntry]:
        if not self.catalog_path.is_file():
            raise LoomcastError(f"Catalog file not found at '{self.catalog_path}'.")

        # NOTE: The catalog SHA-256 checksum file (catalog.json.sha256) must be regenerated
        # using `scripts/generate_catalog_checksum.py` whenever catalog.json is modified intentionally,
        # otherwise StaticCatalog initialization will fail with CatalogIntegrityError.
        checksum_path = self.catalog_path.parent / f"{self.catalog_path.name}.sha256"
        if not checksum_path.is_file():
            raise CatalogIntegrityError(
                f"Checksum file not found at '{checksum_path}'."
            )

        try:
            raw_bytes = self.catalog_path.read_bytes().replace(b"\r\n", b"\n")
            actual_hash = hashlib.sha256(raw_bytes).hexdigest()
            expected_hash = checksum_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            raise CatalogIntegrityError(
                f"Failed to read catalog or checksum file: {e}"
            ) from e

        if actual_hash != expected_hash:
            raise CatalogIntegrityError(
                f"Catalog integrity check failed for '{self.catalog_path}'. "
                f"Expected SHA-256 '{expected_hash}', got '{actual_hash}'."
            )

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise LoomcastError(
                f"Failed to read catalog JSON file '{self.catalog_path}': {e}"
            ) from e

        if not isinstance(data, list):
            raise LoomcastError(
                f"Catalog JSON file '{self.catalog_path}' must contain a list of entries."
            )

        entries: list[CatalogEntry] = []
        for idx, item in enumerate(data):
            try:
                entry = CatalogEntry.model_validate(item)
                entries.append(entry)
            except ValidationError as ve:
                raise LoomcastError(
                    f"Invalid CatalogEntry format at index {idx} in '{self.catalog_path}': {ve}"
                ) from ve

        return entries

    def search(self, query: str) -> list[CatalogEntry]:
        """Search catalog entries matching query in name, description, or tags (case-insensitive)."""
        query_lower = query.lower()
        results: list[CatalogEntry] = []

        for entry in self._entries:
            name_match = query_lower in entry.name.lower()
            desc_match = bool(
                entry.description and query_lower in entry.description.lower()
            )
            tag_match = any(query_lower in tag.lower() for tag in entry.tags)

            if name_match or desc_match or tag_match:
                results.append(entry)

        return results

    def get_entry(self, name: str) -> CatalogEntry | None:
        """Retrieve exact catalog entry by name (case-insensitive comparison)."""
        name_lower = name.lower()
        for entry in self._entries:
            if entry.name.lower() == name_lower:
                return entry
        return None
