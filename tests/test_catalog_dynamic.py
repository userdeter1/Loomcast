import json
import time
from pathlib import Path
import httpx
import pytest

from loomcast.adapters.cache.store import FileSystemCache
from loomcast.adapters.catalog.dynamic import CACHE_SNAPSHOT_KEY, DynamicCatalog, _parse_library_html
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
    assert len(entries) == 2

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


def test_valid_cache_prevents_network_request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that valid cache snapshot avoids making HTTP network requests."""
    cache = FileSystemCache(cache_dir=tmp_path)
    fallback = StaticCatalog()

    # Populate cache with snapshot
    cached_entry = CatalogEntry(
        name="cached-llama",
        description="Cached model desc",
        publisher="ollama",
        tags=["cached"],
        default_runtime=RuntimeType.OLLAMA,
    )
    cache_payload = {
        "timestamp": time.time(),
        "entries": [cached_entry.model_dump()],
    }
    cache.put(CACHE_SNAPSHOT_KEY, json.dumps(cache_payload).encode("utf-8"))

    # Fail test if httpx.get is called
    def mock_get_should_not_be_called(*args, **kwargs):
        pytest.fail("httpx.get should not have been called when valid cache exists")

    monkeypatch.setattr(httpx, "get", mock_get_should_not_be_called)

    catalog = DynamicCatalog(cache=cache, fallback_catalog=fallback, ttl_hours=24)
    results = catalog.search("cached")
    assert len(results) == 1
    assert results[0].name == "cached-llama"

    entry = catalog.get_entry("cached-llama")
    assert entry is not None
    assert entry.name == "cached-llama"


def test_network_failure_falls_back_silently(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
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


def test_successful_scraping_saves_to_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
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
    assert len(cached_data["entries"]) == 2
