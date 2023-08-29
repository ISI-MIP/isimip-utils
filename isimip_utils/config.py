import logging
from pathlib import Path

from colorlog import ColoredFormatter, StreamHandler


class Settings:

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state

    def __str__(self):
        return str(self.args)

    def setup(self, args):
        # assign args to settings object
        self.args = {key.upper(): value for key, value in args.items()}

        # setup logs
        try:
            self.LOG_LEVEL = self.LOG_LEVEL.upper()
            self.LOG_FILE = Path(self.LOG_FILE).expanduser() if self.LOG_FILE else None

            if self.LOG_FILE:
                logging.basicConfig(level=self.LOG_LEVEL, filename=self.LOG_FILE,
                                    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
            else:
                formatter = ColoredFormatter('%(log_color)s[%(asctime)s] %(levelname)s %(name)s: %(message)s')
                handler = StreamHandler()
                handler.setFormatter(formatter)
                logging.basicConfig(level=self.LOG_LEVEL, handlers=[handler])

        except AttributeError:
            pass

    def __getattr__(self, name):
        # this function catches all properties and returns the values in the self.args dict, e.g.
        # settings.FOO -> settings.args['FOO']
        try:
            return self.args[name]
        except KeyError as e:
            raise AttributeError from e
