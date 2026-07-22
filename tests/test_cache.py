import hashlib
import pytest
from pathlib import Path

from loomcast.adapters.cache.store import FileSystemCache
from loomcast.common.exceptions import CacheError
from loomcast.ports.cache import CachePort


def test_file_system_cache_protocol_compliance():
    """Verify that FileSystemCache implements CachePort protocol."""
    cache = FileSystemCache()
    assert isinstance(cache, CachePort)


def test_file_system_cache_put_and_get(tmp_path: Path):
    """Test storing and retrieving data from cache."""
    cache = FileSystemCache(cache_dir=tmp_path)
    key = "test_key_1"
    content = b"sample cached payload data"

    cache.put(key, content)
    retrieved = cache.get(key)
    assert retrieved == content


def test_file_system_cache_get_nonexistent(tmp_path: Path):
    """Test that getting a non-existent key returns None."""
    cache = FileSystemCache(cache_dir=tmp_path)
    assert cache.get("non_existent_key") is None


def test_file_system_cache_exists(tmp_path: Path):
    """Test that exists() correctly reflects the cache state."""
    cache = FileSystemCache(cache_dir=tmp_path)
    key = "check_exists_key"

    assert cache.exists(key) is False
    cache.put(key, b"some content")
    assert cache.exists(key) is True


def test_file_system_cache_compute_key_deterministic():
    """Test that compute_key() is deterministic and produces valid SHA-256 hash."""
    data = b"catalog_scraped_data_content"
    expected_hash = hashlib.sha256(data).hexdigest()

    key1 = FileSystemCache.compute_key(data)
    key2 = FileSystemCache.compute_key(data)

    assert key1 == key2
    assert key1 == expected_hash
    assert key1 != FileSystemCache.compute_key(b"different_content")


def test_file_system_cache_error_handling(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test disk error handling converts OSError to CacheError."""
    cache = FileSystemCache(cache_dir=tmp_path)

    # Test put error handling
    def mock_write_error(self, data):
        raise OSError("Permission denied or disk full")

    monkeypatch.setattr(Path, "write_bytes", mock_write_error)
    with pytest.raises(CacheError):
        cache.put("error_key", b"data")

    # Test get error handling when file exists but reading fails
    monkeypatch.undo()
    cache.put("error_key", b"data")

    def mock_read_error(self):
        raise OSError("Read failure")

    monkeypatch.setattr(Path, "read_bytes", mock_read_error)
    with pytest.raises(CacheError):
        cache.get("error_key")
