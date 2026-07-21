from pathlib import Path
import sys
from typing import Optional

# Standard library TOML support (Python 3.11+) or fallback (Python < 3.11)
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore

import tomli_w  # type: ignore
from pydantic import BaseModel, Field

from common.exceptions import ConfigurationError
from common.paths import get_config_file_path
from domain.entities import RuntimeType


class LoomcastConfig(BaseModel):
    """Loomcast configuration model."""
    default_backend: RuntimeType = Field(default=RuntimeType.OLLAMA)
    catalog_source: str = Field(default="https://ollama.com/library")
    ollama_url: str = Field(default="http://localhost:11434")
    lmstudio_url: str = Field(default="http://localhost:1234")

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "LoomcastConfig":
        """Load configuration from TOML file or return defaults."""
        path = config_path or get_config_file_path()
        if not path.exists():
            config = cls()
            config.save(path)
            return config

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            return cls(**data)
        except Exception as e:
            raise ConfigurationError(f"Failed to parse config file at {path}: {e}") from e

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to TOML file."""
        path = config_path or get_config_file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = self.model_dump(mode="json")
            with open(path, "wb") as f:
                tomli_w.dump(data, f)
        except Exception as e:
            raise ConfigurationError(f"Failed to write config file at {path}: {e}") from e
