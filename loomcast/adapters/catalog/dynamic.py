from __future__ import annotations

import html as html_lib
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

# Bumped to _v2 so snapshots written before the tag-parsing fix (which stored
# pull counters and undecoded entities as tags) are ignored rather than served
# from cache for up to ttl_hours after upgrading.
CACHE_SNAPSHOT_KEY = "catalog_dynamic_snapshot_v2"
MIN_CATALOG_ENTRIES = 5
MAX_TAG_LENGTH = 30

# Pattern matches <a href="/library/<model_name>">...</a>
card_pattern = re.compile(
    r'<a\s+[^>]*href=["\']/library/([a-zA-Z0-9._-]+)["\'][^>]*>(.*?)</a>',
    re.DOTALL | re.IGNORECASE,
)
desc_pattern = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL | re.IGNORECASE)
# Only tag "pills" carry the rounded-md class. A bare <span> match would also
# pick up the card title and the pull-count/updated-at footer.
tag_pattern = re.compile(
    r'<span[^>]*class=["\'][^"\']*rounded-md[^"\']*["\'][^>]*>(.*?)</span>',
    re.DOTALL | re.IGNORECASE,
)
strip_tags_pattern = re.compile(r"<[^>]+>")
svg_pattern = re.compile(r"<svg\b", re.IGNORECASE)
whitespace_pattern = re.compile(r"\s+")
# Case-sensitive on purpose: "117.6M" is a pull counter, "405b" is a model size.
counter_pattern = re.compile(r"^[\d.,]+[KMB]?$")
age_pattern = re.compile(r"^\d+\s+\w+\s+ago$", re.IGNORECASE)

CHROME_WORDS = frozenset({"pulls", "tags", "updated"})


def _clean_text(raw: str) -> str:
    """Strip markup, decode HTML entities, and collapse whitespace."""
    text = strip_tags_pattern.sub("", raw)
    text = html_lib.unescape(text).replace("\xa0", " ")
    return whitespace_pattern.sub(" ", text).strip()


def _is_chrome(tag: str) -> bool:
    """Reject listing-page furniture (pull counts, tag counts, update dates).

    Applied to tags only: descriptions legitimately contain these words, e.g.
    openchat's "Updated to version 3.5-0106."
    """
    return (
        tag.lower() in CHROME_WORDS
        or bool(counter_pattern.match(tag))
        or bool(age_pattern.match(tag))
    )


def _parse_library_html(html: str) -> list[CatalogEntry]:
    """Parse HTML from ollama.com/library into a list of CatalogEntry items."""
    entries: list[CatalogEntry] = []
    seen_names = set()

    for match in card_pattern.finditer(html):
        name = match.group(1).lower()
        if name in seen_names:
            continue
        seen_names.add(name)

        card_content = match.group(2)

        # Extract description from the first <p> that is not the stats footer
        # (the footer is the only <p> carrying inline <svg> icons).
        description = None
        for d_match in desc_pattern.finditer(card_content):
            if svg_pattern.search(d_match.group(1)):
                continue
            clean_desc = _clean_text(d_match.group(1))
            if clean_desc:
                description = clean_desc
                break

        # Extract tags from pill <span> elements
        tags: list[str] = []
        for t_match in tag_pattern.finditer(card_content):
            clean_tag = _clean_text(t_match.group(1))
            if (
                clean_tag
                and len(clean_tag) < MAX_TAG_LENGTH
                and not _is_chrome(clean_tag)
                and clean_tag.lower() != name
                and clean_tag not in tags
            ):
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
                f"Scraped content invalid or suspicious, falling back to the static catalog: {e}"
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
