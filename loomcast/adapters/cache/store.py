import hashlib
from pathlib import Path
from typing import Optional, Union

from loomcast.common.exceptions import CacheError
from loomcast.common.paths import get_cache_dir
from loomcast.ports.cache import CachePort


class FileSystemCache(CachePort):
    """File system implementation of CachePort."""

    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        if cache_dir is None:
            self.cache_dir = get_cache_dir()
        else:
            self.cache_dir = Path(cache_dir)

        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise CacheError(
                f"Failed to create cache directory '{self.cache_dir}': {e}"
            ) from e

    def _get_path(self, key: str) -> Path:
        return self.cache_dir / key

    def get(self, key: str) -> Optional[bytes]:
        """Retrieve cached bytes by key, returning None if non-existent."""
        path = self._get_path(key)
        if not path.is_file():
            return None
        try:
            return path.read_bytes()
        except OSError as e:
            raise CacheError(f"Failed to read cache entry '{key}': {e}") from e

    def put(self, key: str, value: bytes) -> None:
        """Store bytes into cache under key."""
        path = self._get_path(key)
        try:
            path.write_bytes(value)
        except OSError as e:
            raise CacheError(f"Failed to write cache entry '{key}': {e}") from e

    def exists(self, key: str) -> bool:
        """Check if key exists in cache without reading contents."""
        path = self._get_path(key)
        try:
            return path.is_file()
        except OSError as e:
            raise CacheError(
                f"Failed to check existence for cache entry '{key}': {e}"
            ) from e

    @staticmethod
    def compute_key(data: bytes) -> str:
        """Compute hexadecimal SHA-256 hash of content."""
        return hashlib.sha256(data).hexdigest()
