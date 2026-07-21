from pathlib import Path
import platformdirs

APP_NAME = "loomcast"


def get_config_dir() -> Path:
    """Return the cross-platform configuration directory."""
    config_dir = Path(platformdirs.user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file_path() -> Path:
    """Return the default config file path (~/.config/loomcast/config.toml or OS equivalent)."""
    # Prefer explicitly ~/.config/loomcast/config.toml if present or default config dir
    home_config = Path.home() / ".config" / APP_NAME / "config.toml"
    if home_config.exists():
        return home_config
    
    config_dir = get_config_dir()
    return config_dir / "config.toml"


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
