import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Set

# Standard library TOML support (Python 3.11+) or fallback (Python < 3.11)
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore

import tomli_w  # type: ignore
from pydantic import BaseModel, Field, PrivateAttr

from loomcast.common.exceptions import ConfigurationError
from loomcast.common.paths import get_config_file_path
from loomcast.domain.entities import RuntimeType


class LoomcastConfig(BaseModel):
    """Loomcast configuration model."""
    default_backend: RuntimeType = Field(default=RuntimeType.OLLAMA)
    catalog_source: str = Field(default="https://ollama.com/library")
    ollama_url: str = Field(default="http://localhost:11434")
    lmstudio_url: str = Field(default="http://localhost:1234")
    llamacpp_url: str = Field(default="http://localhost:8080")

    _file_data: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _env_keys: Set[str] = PrivateAttr(default_factory=set)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "LoomcastConfig":
        """Load configuration from TOML file or return defaults, applying environment variable overrides."""
        path = config_path or get_config_file_path()
        if not path.exists():
            config = cls()
            file_data = config.model_dump(mode="json")
            config.save(path)
        else:
            try:
                with open(path, "rb") as f:
                    file_data = tomllib.load(f)
                config = cls(**file_data)
            except Exception as e:
                raise ConfigurationError(f"Failed to parse config file at {path}: {e}") from e

        config._file_data = dict(file_data)
        config._env_keys = set()

        env_mapping = {
            "LOOMCAST_DEFAULT_BACKEND": "default_backend",
            "LOOMCAST_OLLAMA_URL": "ollama_url",
            "LOOMCAST_LMSTUDIO_URL": "lmstudio_url",
            "LOOMCAST_LLAMACPP_URL": "llamacpp_url",
            "LOOMCAST_CATALOG_SOURCE": "catalog_source",
        }

        for env_var, field_name in env_mapping.items():
            if env_var in os.environ:
                val = os.environ[env_var]
                try:
                    temp_data = config.model_dump()
                    temp_data[field_name] = val
                    validated = cls(**temp_data)
                    validated_val = getattr(validated, field_name)
                    setattr(config, field_name, validated_val)
                    config._env_keys.add(field_name)
                except Exception as e:
                    raise ConfigurationError(
                        f"Invalid environment variable '{env_var}': '{val}'. {e}"
                    ) from e

        return config

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to TOML file without persisting environment variable overrides."""
        path = config_path or get_config_file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = self.model_dump(mode="json")
            for field_name in self._env_keys:
                if field_name in self._file_data:
                    data[field_name] = self._file_data[field_name]
                else:
                    default_instance = self.__class__()
                    data[field_name] = default_instance.model_dump(mode="json")[field_name]

            with open(path, "wb") as f:
                tomli_w.dump(data, f)
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Failed to write config file at {path}: {e}") from e
