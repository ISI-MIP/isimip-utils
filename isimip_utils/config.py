import configparser
import logging
import os
from pathlib import Path

from colorlog import ColoredFormatter, StreamHandler
from dotenv import load_dotenv


class ISIMIPSettings(object):

    _shared_state = {}

    CONFIG_FILES = [
        'isimip.conf',
        '~/.isimip.conf',
        '/etc/isimip.conf'
    ]

    def __init__(self):
        self.__dict__ = self._shared_state

    def __str__(self):
        return str(vars(self))

    def setup(self, parser):
        args = parser.parse_args()

        # store the parser for later use
        self.parser = parser

        # setup env from .env file
        load_dotenv(Path().cwd() / '.env')

        # read config file
        config = self.read_config(parser, args)

        # combine settings from os.environ and config to create defaults
        self.build_settings(parser, args, os.environ, config)

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

    def read_config(self, parser, args):
        config_files = [args.config_file] + self.CONFIG_FILES
        for config_file in config_files:
            if config_file:
                config = configparser.ConfigParser()
                config.read(config_file)
                if parser.prog in config:
                    return config[parser.prog]

    def build_settings(self, parser, args, environ, config):
        args_dict = vars(args)
        for key, value in args_dict.items():
            default = parser.get_default(key)
            key_upper = key.upper()
            if value == default:
                # if the value is the default it was not set by the command line
                # so we look if it is in the environment or in the config
                if environ.get(key_upper):
                    # if the attribute is in the environment, take the value
                    value = environ.get(key_upper)
                elif config and config.get(key):
                    # if the attribute is in the config file, take it from there
                    value = config.get(key)

            setattr(self, key_upper, value)
