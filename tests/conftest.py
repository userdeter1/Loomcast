from pathlib import Path

import pytest

from loomcast.common.config import LoomcastConfig
from loomcast.domain.entities import RuntimeType


@pytest.fixture
def tmp_config_file(tmp_path: Path) -> Path:
    """Fixture providing a temporary config file path."""
    return tmp_path / "config.toml"


@pytest.fixture
def sample_config() -> LoomcastConfig:
    """Fixture providing a sample LoomcastConfig instance."""
    return LoomcastConfig(
        default_backend=RuntimeType.OLLAMA,
        catalog_source="https://test.catalog/library",
        ollama_url="http://localhost:11434",
        lmstudio_url="http://localhost:1234",
    )
