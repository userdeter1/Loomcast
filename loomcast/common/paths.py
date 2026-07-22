from pathlib import Path
import platformdirs

APP_NAME = "loomcast"


def get_config_dir() -> Path:
    """Return the cross-platform configuration directory."""
    config_dir = Path(platformdirs.user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file_path() -> Path:
    """Return the default cross-platform config file path."""
    return get_config_dir() / "config.toml"



def get_cache_dir() -> Path:
    """Return the cross-platform cache directory."""
    cache_dir = Path(platformdirs.user_cache_dir(APP_NAME))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_data_dir() -> Path:
    """Return the cross-platform data directory."""
    data_dir = Path(platformdirs.user_data_dir(APP_NAME))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
