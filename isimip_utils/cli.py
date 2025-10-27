"""Command-line interface utilities for ISIMIP tools."""
import argparse
import logging
import os
import tomllib
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.logging import RichHandler

from .exceptions import ConfigError


def setup_env() -> None:
    """Load environment variables from .env file in current working directory."""
    load_dotenv(Path().cwd() / '.env')


def setup_logs(log_level: str = 'WARN', log_file: str | None = None,
               log_console: bool = True, log_rich: bool = True) -> None:
    """Configure logging with console and/or file handlers.

    Args:
        log_level (str): Logging level (default: 'WARN').
        log_file (str | None): Path to log file, or None for no file logging (default: None).
        log_console (bool): Whether to log to console (default: True).
        log_rich (bool): Whether to use RichHandler for console logging (default: True).
    """
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


def parse_dict(string: str) -> dict[str, list[str]]:
    """Parse a string in format 'key=value1,value2' into a dictionary.

    Args:
        string (str): String to parse in format 'key=value1,value2,value3'.

    Returns:
        Dictionary with single key mapping to list of values.
    """
    key, values = string.split('=')
    return {
        key.strip(): [value.strip() for value in values.split(',')]
    }


def parse_list(string: str) -> list[str]:
    """Parse a comma-separated string into a list.

    Args:
        string (str): Comma-separated string to parse.

    Returns:
        List of stripped values.
    """
    return [value.strip() for value in string.split(',')]


def parse_version(value: str) -> datetime:
    """Parse a version string in YYYYMMDD format.

    Args:
        value (str): Version string in YYYYMMDD format.

    Returns:
        Parsed datetime object.

    Raises:
        argparse.ArgumentTypeError: If format is incorrect.
    """
    try:
        return datetime.strptime(value, '%Y%m%d')
    except ValueError as e:
        raise argparse.ArgumentTypeError('incorrect format, should be YYYYMMDD') from e


def parse_path(value: str) -> Path:
    """Parse and expand a path string.

    Args:
        value (str): Path string to parse.

    Returns:
        Expanded Path object.
    """
    return Path(value).expanduser()


class ArgumentParser(argparse.ArgumentParser):
    """Extended ArgumentParser that reads defaults from config files and environment.

    Supports reading configuration from TOML files in the following order:

    - `./isimip.toml`
    - `~/.isimip.toml`
    - `/etc/isimip.toml`

    Environment variables (uppercase) override config file values.
    """

    config_files = [
        'isimip.toml',
        '~/.isimip.toml',
        '/etc/isimip.toml',
    ]

    def parse_args(self, *args) -> argparse.Namespace:
        return super().parse_args(*args, namespace=self.build_default_args())

    def get_defaults(self) -> dict:
        defaults = {}
        for action in self._actions:
            if not action.required and action.dest != 'help':
                defaults[action.dest] = action.default

        defaults.update(vars(self.build_default_args()))
        return defaults

    def read_config(self) -> dict:
        for config_file in self.config_files:
            config_path = Path(config_file).expanduser()
            if config_path.is_file():
                with open(config_path, 'rb') as fp:
                    data = tomllib.load(fp)
                    if self.prog in data:
                        return data[self.prog]
        return {}

    def build_default_args(self) -> argparse.Namespace:
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
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.lower() == 'none':
                        value = None

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
