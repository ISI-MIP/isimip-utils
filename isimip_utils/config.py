import logging

from .utils import Singleton

logger = logging.getLogger(__name__)


class Settings(Singleton):
    _settings = {}

    def __repr__(self):
        return str(self._settings)

    def __getattr__(self, name):
        if name in self._settings.keys():
            return self._settings[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            # allow normal attribute for internal data
            super().__setattr__(name, value)
        else:
            self._settings[name] = value

    def dict(self):
        return self._settings

    @classmethod
    def from_dict(cls, values):
        instance = cls()
        instance._settings = {key.upper(): value for key, value in values.items()}
        logger.debug('settings = %s', instance)
        return instance
