import argparse
import configparser
import os
from pathlib import Path

from dotenv import load_dotenv


class ArgumentParser(argparse.ArgumentParser):

    CONFIG_FILES = [
        'isimip.conf',
        '~/.isimip.conf',
        '/etc/isimip.conf'
    ]

    def parse_args(self, *args):
        # parse the command line arguments with the default namespace
        # obtained from the config file and the environment
        return super().parse_args(*args, namespace=self.build_default_args())

    def get_defaults(self):
        defaults = {}
        for action in self._actions:
            if not action.required and action.dest != 'help':
                defaults[action.dest] = action.default

        defaults.update(vars(self.build_default_args()))
        return defaults

    def read_config(self):
        for config_file in self.CONFIG_FILES:
            config_path = Path(config_file).expanduser()

            config = configparser.ConfigParser()
            config.read(config_path)
            if self.prog in config:
                return config[self.prog]

    def build_default_args(self):
        # setup env from .env file
        load_dotenv(Path().cwd() / '.env')

        # read config file
        config = self.read_config()

        # init the default namespace
        default_args = argparse.Namespace()

        for action in self._actions:
            if not action.required and action.dest != 'help':
                key = action.dest
                key_upper = key.upper()
                if os.getenv(key_upper):
                    # if the attribute is in the environment, take the value
                    setattr(default_args, key, os.getenv(key_upper))
                elif config and config.get(key):
                    # if the attribute is in the config file, take it from there
                    setattr(default_args, key, config.get(key))

        return default_args
