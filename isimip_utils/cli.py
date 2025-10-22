import argparse
import logging
import os
import tomllib
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.logging import RichHandler

from .exceptions import ConfigError


def setup_env():
    load_dotenv(Path().cwd() / '.env')


def setup_logs(log_level='WARN', log_file=None, log_console=True, log_rich=True):
    log_level = log_level.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if log_console:
        if log_rich:
            console_handler = RichHandler()
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

    if log_file is not None:
        Path(log_file).parent.mkdir(exist_ok=True, parents=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

        root_logger.addHandler(file_handler)


def parse_dict(string):
    key, values = string.split('=')
    return {
        key.strip(): [value.strip() for value in values.split(',')]
    }


def parse_list(string):
    return [value.strip() for value in string.split(',')]


def parse_version(value):
    try:
        return datetime.strptime(value, '%Y%m%d')
    except ValueError as e:
        raise argparse.ArgumentTypeError('incorrect format, should be YYYYMMDD') from e


def parse_path(value):
    return Path(value).expanduser()


class ArgumentParser(argparse.ArgumentParser):

    config_files = [
        'isimip.toml',
        '~/.isimip.toml',
        '/etc/isimip.toml',
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
        for config_file in self.config_files:
            config_path = Path(config_file).expanduser()
            if config_path.is_file():
                with open(config_path, 'rb') as fp:
                    data = tomllib.load(fp)
                    if self.prog in data:
                        return data[self.prog]
        return {}

    def build_default_args(self):
        # read config file
        config = self.read_config()

        # init the default namespace
        default_args = argparse.Namespace()

        for action in self._actions:
            if not action.required and action.dest != 'help':
                key = action.dest
                key_upper = key.upper()

                value = None

                if os.getenv(key_upper):
                    # if the attribute is in the environment, take the value
                    value = os.getenv(key_upper)
                    # setattr(default_args, key, )
                elif config and key in config:
                    # if the attribute is in the config file, take it from there
                    value = config.get(key)

                if value is not None:
                    # apply action.type
                    if action.type is not None:
                        try:
                            value = action.type(value)
                        except argparse.ArgumentTypeError as e:
                            raise ConfigError(f'argument "{key}": {e}') from e

                    # check action.action
                    if action.const and value not in [True, False]:
                        raise ConfigError(f'argument "{key}": invalid choice "{value}" (choose true or false)')

                    # check action.choices
                    if action.choices and value not in action.choices:
                        raise ConfigError(f'argument "{key}": invalid choice "{value}" (choose from {action.choices})')

                    # add the key and value to the default_args
                    setattr(default_args, key, value)

        return default_args
