"""Configuration management for ISIMIP tools."""
import logging
import tomllib
from typing import Any

from .utils import Singleton

logger = logging.getLogger(__name__)


class Settings(Singleton):
    """Singleton settings class for managing application configuration.

    This class provides a centralized settings store that combines input from
    argparse, environment variables, and config files. Settings are stored as
    uppercase keys and can be accessed as attributes.
    """
    _settings: dict[str, Any] = {}

    ignore_keys = ('config', )

    def __repr__(self) -> str:
        return str(self._settings)

    def __getattr__(self, name: str) -> Any:
        if name in self._settings.keys():
            return self._settings[name]
        else:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            # allow normal attribute for internal data
            super().__setattr__(name, value)
        else:
            self._settings[name] = value

    def to_dict(self) -> dict[str, Any]:
        """Return the settings as a dictionary.

        Returns:
            Dictionary of all settings.
        """
        return self._settings

    def update(self, values: dict[str, Any]) -> dict[str, Any]:
        """Update the settings from a dictionary.

        Args:
            values (dict[str, Any]): Dictionary of setting key-value pairs.
        """
        for key, value in values.items():
            name = key.upper()
            current_value = self._settings[name]

            if not hasattr(self, name):
                raise ValueError(f'unknown key "{key}"')

            if isinstance(current_value, list):
                current_value.extend(value if isinstance(value, list) else [value])
            elif isinstance(current_value, dict):
                if not isinstance(value, dict):
                    raise ValueError(f'key "{key}" is not a dict')
                self._settings[name].update(value)
            else:
                self._settings[name] = value


    def update_from_toml(self, path):
        """Update the settings from a toml file..

        Args:
            path (Path): Path to the toml file/.
        """
        if path and path.exists():
            config = tomllib.loads(path.read_text())
            self.update(config)


    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> 'Settings':
        """Create a Settings instance from a dictionary.

        Args:
            values (dict[str, Any]): Dictionary of setting key-value pairs.

        Returns:
            A Settings instance populated with the provided values.
            All keys are converted to uppercase.
        """
        instance = cls()
        instance._settings = {key.upper(): value for key, value in values.items() if key not in cls.ignore_keys}
        logger.debug('settings = %s', instance)
        return instance
