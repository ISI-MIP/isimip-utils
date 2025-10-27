"""Configuration management for ISIMIP tools."""
import logging
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

    def __repr__(self) -> str:
        return str(self._settings)

    def __getattr__(self, name: str) -> Any:
        if name in self._settings.keys():
            return self._settings[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            # allow normal attribute for internal data
            super().__setattr__(name, value)
        else:
            self._settings[name] = value

    def dict(self) -> dict[str, Any]:
        """Return the settings as a dictionary.

        Returns:
            Dictionary of all settings.
        """
        return self._settings

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
        instance._settings = {key.upper(): value for key, value in values.items()}
        logger.debug('settings = %s', instance)
        return instance
