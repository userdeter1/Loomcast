import json
import time
from pathlib import Path
import httpx
import pytest

from loomcast.adapters.cache.store import FileSystemCache
from loomcast.adapters.catalog.dynamic import (
    CACHE_SNAPSHOT_KEY,
    DynamicCatalog,
    _parse_library_html,
)
from loomcast.adapters.catalog.static import StaticCatalog
from loomcast.domain.entities import CatalogEntry, RuntimeType
from loomcast.ports.catalog import CatalogPort


SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<body>
<div id="repo">
  <a href="/library/llama3" class="group">
    <h2>llama3</h2>
    <p>Meta's state-of-the-art model for reasoning</p>
    <span>8B</span>
    <span>70B</span>
  </a>
  <a href="/library/deepseek-coder" class="group">
    <h2>deepseek-coder</h2>
    <p>DeepSeek Coder open-source code language model</p>
    <span>code</span>
  </a>
  <a href="/library/mistral" class="group">
    <h2>mistral</h2>
    <p>7B model by Mistral AI</p>
    <span>general</span>
  </a>
  <a href="/library/phi3" class="group">
    <h2>phi3</h2>
    <p>Microsoft lightweight model</p>
    <span>mini</span>
  </a>
  <a href="/library/gemma" class="group">
    <h2>gemma</h2>
    <p>Google open weight model</p>
    <span>google</span>
  </a>
</div>
</body>
</html>
"""

SHORT_HTML = """
<!DOCTYPE html>
<html>
<body>
<div id="repo">
  <a href="/library/llama3" class="group">
    <h2>llama3</h2>
    <p>Short list model 1</p>
  </a>
  <a href="/library/deepseek-coder" class="group">
    <h2>deepseek-coder</h2>
    <p>Short list model 2</p>
  </a>
</div>
</body>
</html>
"""


def test_dynamic_catalog_protocol_compliance(tmp_path: Path):
    """Verify that DynamicCatalog complies with CatalogPort protocol."""
    cache = FileSystemCache(cache_dir=tmp_path)
    fallback = StaticCatalog()
    catalog = DynamicCatalog(cache=cache, fallback_catalog=fallback)
    assert isinstance(catalog, CatalogPort)


def test_parse_library_html():
    """Test HTML parser correctly extracts models, descriptions, and tags."""
    entries = _parse_library_html(SAMPLE_HTML)
    assert len(entries) == 5

    llama = entries[0]
    assert llama.name == "llama3"
    assert llama.description == "Meta's state-of-the-art model for reasoning"
    assert "8B" in llama.tags
    assert llama.publisher == "ollama"
    assert llama.default_runtime == RuntimeType.OLLAMA

    coder = entries[1]
    assert coder.name == "deepseek-coder"
    assert coder.description == "DeepSeek Coder open-source code language model"
    assert "code" in coder.tags


def test_valid_cache_prevents_network_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that valid cache snapshot avoids making HTTP network requests."""
    cache = FileSystemCache(cache_dir=tmp_path)
    fallback = StaticCatalog()

    # Populate cache with snapshot (at least MIN_CATALOG_ENTRIES=5)
    cached_entries = [
        CatalogEntry(
            name=f"cached-model-{i}",
            description=f"Cached model desc {i}",
            publisher="ollama",
            tags=["cached"],
            default_runtime=RuntimeType.OLLAMA,
        )
        for i in range(5)
    ]
    cache_payload = {
        "timestamp": time.time(),
        "entries": [e.model_dump() for e in cached_entries],
    }
    cache.put(CACHE_SNAPSHOT_KEY, json.dumps(cache_payload).encode("utf-8"))

    # Fail test if httpx.get is called
    def mock_get_should_not_be_called(*args, **kwargs):
        pytest.fail("httpx.get should not have been called when valid cache exists")

    monkeypatch.setattr(httpx, "get", mock_get_should_not_be_called)

    catalog = DynamicCatalog(cache=cache, fallback_catalog=fallback, ttl_hours=24)
    results = catalog.search("cached")
    assert len(results) == 5
    assert results[0].name == "cached-model-0"

    entry = catalog.get_entry("cached-model-0")
    assert entry is not None
    assert entry.name == "cached-model-0"


def test_network_failure_falls_back_silently(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that network error triggers silent fallback to StaticCatalog without raising exceptions."""
    cache = FileSystemCache(cache_dir=tmp_path)
    fallback = StaticCatalog()

    def mock_get_network_error(*args, **kwargs):
        raise httpx.ConnectError("Connection timed out")

    monkeypatch.setattr(httpx, "get", mock_get_network_error)

    catalog = DynamicCatalog(cache=cache, fallback_catalog=fallback)

    # Should not raise exception, should fall back to StaticCatalog entries
    results = catalog.search("code")
    assert len(results) > 0
    names = [e.name for e in results]
    assert "codellama" in names

    get_res = catalog.get_entry("mistral")
    assert get_res is not None
    assert get_res.name == "mistral"


def test_successful_scraping_saves_to_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that successful HTTP scraping parses entries and saves them to cache."""
    cache = FileSystemCache(cache_dir=tmp_path)
    fallback = StaticCatalog()

    def mock_get_success(url, **kwargs):
        return httpx.Response(200, text=SAMPLE_HTML)

    monkeypatch.setattr(httpx, "get", mock_get_success)

    catalog = DynamicCatalog(cache=cache, fallback_catalog=fallback)
    results = catalog.search("llama3")

    assert len(results) == 1
    assert results[0].name == "llama3"

    # Verify cache snapshot was populated
    raw_cache = cache.get(CACHE_SNAPSHOT_KEY)
    assert raw_cache is not None
    cached_data = json.loads(raw_cache.decode("utf-8"))
    assert "timestamp" in cached_data
    assert len(cached_data["entries"]) == 5


def test_dynamic_catalog_fallback_on_insufficient_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that HTML parsing returning fewer than MIN_CATALOG_ENTRIES (5) triggers static catalog fallback."""
    cache = FileSystemCache(cache_dir=tmp_path)
    fallback = StaticCatalog()

    def mock_get_short_html(url, **kwargs):
        return httpx.Response(200, text=SHORT_HTML)

    monkeypatch.setattr(httpx, "get", mock_get_short_html)

    catalog = DynamicCatalog(cache=cache, fallback_catalog=fallback)

    # Search should fall back to static catalog without raising exception
    results = catalog.search("codellama")
    assert len(results) > 0
    assert any(e.name == "codellama" for e in results)


def test_dynamic_catalog_fallback_on_invalid_pydantic_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that HTML parsing producing invalid Pydantic entry triggers static catalog fallback."""
    cache = FileSystemCache(cache_dir=tmp_path)
    fallback = StaticCatalog()

    def mock_get_success(url, **kwargs):
        return httpx.Response(200, text=SAMPLE_HTML)

    monkeypatch.setattr(httpx, "get", mock_get_success)

    # Monkeypatch _parse_library_html to raise ValueError (simulating Pydantic validation failure)
    def mock_parse_invalid(html: str):
        raise ValueError("Invalid entry field: name cannot be empty")

    monkeypatch.setattr(
        "loomcast.adapters.catalog.dynamic._parse_library_html", mock_parse_invalid
    )

    catalog = DynamicCatalog(cache=cache, fallback_catalog=fallback)

    # Should fall back gracefully to static catalog without raising exception
    results = catalog.search("mistral")
    assert len(results) > 0
    assert any(e.name == "mistral" for e in results)
