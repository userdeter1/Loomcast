import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore

import pytest

from loomcast.common.config import LoomcastConfig
from loomcast.common.exceptions import ConfigurationError
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


def test_env_var_overrides_toml_value(tmp_path: Path, monkeypatch):
    config_file = tmp_path / "config.toml"
    initial_config = LoomcastConfig(
        default_backend=RuntimeType.OLLAMA,
        ollama_url="http://localhost:11434",
    )
    initial_config.save(config_file)

    monkeypatch.setenv("LOOMCAST_DEFAULT_BACKEND", "lmstudio")
    monkeypatch.setenv("LOOMCAST_OLLAMA_URL", "http://env-host:11434")

    loaded = LoomcastConfig.load(config_file)
    assert loaded.default_backend == RuntimeType.LMSTUDIO
    assert loaded.ollama_url == "http://env-host:11434"


def test_invalid_env_var_raises_configuration_error(tmp_path: Path, monkeypatch):
    config_file = tmp_path / "config.toml"

    monkeypatch.setenv("LOOMCAST_DEFAULT_BACKEND", "invalid_backend_name")

    with pytest.raises(ConfigurationError) as exc_info:
        LoomcastConfig.load(config_file)

    assert "LOOMCAST_DEFAULT_BACKEND" in str(exc_info.value)


def test_save_does_not_persist_env_var_override(tmp_path: Path, monkeypatch):
    config_file = tmp_path / "config.toml"
    initial_config = LoomcastConfig(
        default_backend=RuntimeType.OLLAMA,
        ollama_url="http://localhost:11434",
    )
    initial_config.save(config_file)

    monkeypatch.setenv("LOOMCAST_DEFAULT_BACKEND", "lmstudio")
    monkeypatch.setenv("LOOMCAST_OLLAMA_URL", "http://override:11434")

    loaded = LoomcastConfig.load(config_file)
    assert loaded.default_backend == RuntimeType.LMSTUDIO
    assert loaded.ollama_url == "http://override:11434"

    # Save loaded config instance
    loaded.save(config_file)

    # Read raw file content to verify env vars were NOT persisted
    with open(config_file, "rb") as f:
        data = tomllib.load(f)

    assert data["default_backend"] == "ollama"
    assert data["ollama_url"] == "http://localhost:11434"


def test_no_env_var_non_regression(tmp_path: Path, monkeypatch):
    for var in [
        "LOOMCAST_DEFAULT_BACKEND",
        "LOOMCAST_OLLAMA_URL",
        "LOOMCAST_LMSTUDIO_URL",
        "LOOMCAST_CATALOG_SOURCE",
    ]:
        monkeypatch.delenv(var, raising=False)

    config_file = tmp_path / "config.toml"
    initial_config = LoomcastConfig(
        default_backend=RuntimeType.LMSTUDIO,
        catalog_source="https://example.com/catalog",
    )
    initial_config.save(config_file)

    loaded = LoomcastConfig.load(config_file)
    assert loaded.default_backend == RuntimeType.LMSTUDIO
    assert loaded.catalog_source == "https://example.com/catalog"
    assert loaded.ollama_url == "http://localhost:11434"
