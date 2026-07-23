from __future__ import annotations

import json
import re
import time

import httpx
from pydantic import ValidationError

from loomcast.adapters.cache.store import FileSystemCache
from loomcast.adapters.catalog.static import StaticCatalog
from loomcast.common.logging import logger
from loomcast.domain.entities import CatalogEntry, RuntimeType
from loomcast.ports.cache import CachePort
from loomcast.ports.catalog import CatalogPort

CACHE_SNAPSHOT_KEY = "catalog_dynamic_snapshot"
MIN_CATALOG_ENTRIES = 5


def _parse_library_html(html: str) -> list[CatalogEntry]:
    """Parse HTML from ollama.com/library into a list of CatalogEntry items."""
    entries: list[CatalogEntry] = []
    seen_names = set()

    # Pattern matches <a href="/library/<model_name>">...</a>
    card_pattern = re.compile(
        r'<a\s+[^>]*href=["\']/library/([a-zA-Z0-9._-]+)["\'][^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE,
    )
    desc_pattern = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL | re.IGNORECASE)
    tag_pattern = re.compile(r"<span[^>]*>(.*?)</span>", re.DOTALL | re.IGNORECASE)
    strip_tags_pattern = re.compile(r"<[^>]+>")

    for match in card_pattern.finditer(html):
        name = match.group(1).lower()
        if name in seen_names:
            continue
        seen_names.add(name)

        card_content = match.group(2)

        # Extract description from <p>
        desc_match = desc_pattern.search(card_content)
        description = None
        if desc_match:
            clean_desc = strip_tags_pattern.sub("", desc_match.group(1)).strip()
            if clean_desc:
                description = clean_desc

        # Extract tags from <span>
        tags = []
        for t_match in tag_pattern.finditer(card_content):
            clean_tag = strip_tags_pattern.sub("", t_match.group(1)).strip()
            if clean_tag and len(clean_tag) < 30:
                tags.append(clean_tag)

        if not tags:
            tags = ["ollama"]

        try:
            entry = CatalogEntry(
                name=name,
                description=description,
                publisher="ollama",
                tags=tags,
                default_runtime=RuntimeType.OLLAMA,
            )
            entries.append(entry)
        except ValidationError as ve:
            raise ValueError(f"Invalid parsed entry '{name}': {ve}") from ve

    return entries


class DynamicCatalog(CatalogPort):
    """Dynamic CatalogPort implementation with TTL caching and static fallback."""

    def __init__(
        self,
        cache: CachePort | None = None,
        fallback_catalog: CatalogPort | None = None,
        ttl_hours: int = 24,
    ):
        self.cache: CachePort = cache if cache is not None else FileSystemCache()
        self.fallback_catalog: CatalogPort = (
            fallback_catalog if fallback_catalog is not None else StaticCatalog()
        )
        self.ttl_hours = ttl_hours

    def _get_entries(self) -> tuple[list[CatalogEntry] | None, bool]:
        """Fetch entries from cache or network, or indicate fallback required."""
        # 1. Try cache
        raw_cache = self.cache.get(CACHE_SNAPSHOT_KEY)
        if raw_cache:
            try:
                data = json.loads(raw_cache.decode("utf-8"))
                timestamp = data.get("timestamp", 0)
                if (time.time() - timestamp) < (self.ttl_hours * 3600):
                    entries_data = data.get("entries", [])
                    entries = [
                        CatalogEntry.model_validate(item) for item in entries_data
                    ]
                    if len(entries) >= MIN_CATALOG_ENTRIES:
                        return entries, False
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to read dynamic catalog cache snapshot: {e}")

        # 2. Try scraping Ollama library
        try:
            response = httpx.get("https://ollama.com/library", timeout=10.0)
            if response.status_code != 200:
                raise ValueError(f"HTTP error status code {response.status_code}")
            entries = _parse_library_html(response.text)

            # Minimum consistency validation: check threshold count and Pydantic validation
            if len(entries) < MIN_CATALOG_ENTRIES:
                raise ValueError(
                    f"Parsed entries count ({len(entries)}) is below minimum threshold ({MIN_CATALOG_ENTRIES})"
                )

            for idx, entry in enumerate(entries):
                try:
                    CatalogEntry.model_validate(entry.model_dump())
                except ValidationError as ve:
                    raise ValueError(
                        f"CatalogEntry validation failed at index {idx}: {ve}"
                    ) from ve

            # Save snapshot to cache
            cache_payload = {
                "timestamp": time.time(),
                "entries": [e.model_dump() for e in entries],
            }
            self.cache.put(
                CACHE_SNAPSHOT_KEY, json.dumps(cache_payload).encode("utf-8")
            )
            return entries, False
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"Contenu scrapé invalide ou suspect, basculement sur le catalogue statique: {e}"
            )
            return None, True

    def search(self, query: str) -> list[CatalogEntry]:
        """Search catalog for entries matching query, falling back to static catalog if needed."""
        entries, is_fallback = self._get_entries()
        if is_fallback or entries is None:
            return self.fallback_catalog.search(query)

        query_lower = query.lower()
        results: list[CatalogEntry] = []
        for entry in entries:
            name_match = query_lower in entry.name.lower()
            desc_match = bool(
                entry.description and query_lower in entry.description.lower()
            )
            tag_match = any(query_lower in tag.lower() for tag in entry.tags)

            if name_match or desc_match or tag_match:
                results.append(entry)

        return results

    def get_entry(self, name: str) -> CatalogEntry | None:
        """Retrieve catalog entry by name, falling back to static catalog if needed."""
        entries, is_fallback = self._get_entries()
        if is_fallback or entries is None:
            return self.fallback_catalog.get_entry(name)

        name_lower = name.lower()
        for entry in entries:
            if entry.name.lower() == name_lower:
                return entry
        return None
