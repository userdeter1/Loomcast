from pathlib import Path
import pytest
from loomcast.common.config import LoomcastConfig
from loomcast.common.paths import get_config_dir, get_config_file_path
from loomcast.domain.entities import RuntimeType


def test_config_defaults():
    config = LoomcastConfig()
    assert config.default_backend == RuntimeType.OLLAMA
    assert "ollama.com" in config.catalog_source
    assert config.ollama_url == "http://localhost:11434"
    assert config.lmstudio_url == "http://localhost:1234"


def test_config_save_and_load(tmp_config_file: Path):
    config = LoomcastConfig(
        default_backend=RuntimeType.LMSTUDIO,
        catalog_source="https://custom.catalog/source",
        ollama_url="http://127.0.0.1:11434",
        lmstudio_url="http://127.0.0.1:1234",
    )
    config.save(tmp_config_file)
    assert tmp_config_file.exists()

    loaded = LoomcastConfig.load(tmp_config_file)
    assert loaded.default_backend == RuntimeType.LMSTUDIO
    assert loaded.catalog_source == "https://custom.catalog/source"
    assert loaded.ollama_url == "http://127.0.0.1:11434"
    assert loaded.lmstudio_url == "http://127.0.0.1:1234"


def test_paths_helpers():
    config_dir = get_config_dir()
    assert isinstance(config_dir, Path)
    config_file = get_config_file_path()
    assert isinstance(config_file, Path)
    assert config_file.name == "config.toml"
