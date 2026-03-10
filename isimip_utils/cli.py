"""Command-line interface utilities for ISIMIP tools."""
import argparse
import logging
import os
import tomllib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from rich.logging import RichHandler

from .exceptions import ConfigError


def setup_env() -> None:
    """Load environment variables from .env file in current working directory."""
    load_dotenv(Path().cwd() / '.env')


def setup_logs(log_level: str = 'WARNING', log_file: str | None = None,
               log_console: bool = True, log_rich: bool = True,
               show_time: bool = False, show_path: bool = False) -> None:
    """Configure logging with console and/or file handlers.

    Args:
        log_level (str): Logging level (default: 'WARNING').
        log_file (str | None): Path to log file, or None for no file logging (default: None).
        log_console (bool): Whether to log to console (default: True).
        log_rich (bool): Whether to use RichHandler for console logging (default: True).
        show_time (bool): Whether to show the time in the console logs (default: False).
        show_path (bool): Whether to show the path in the console logs (default: False).
    """
    log_level = log_level.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if log_console:
        if log_rich:
            console_handler = RichHandler(show_time=show_time, show_path=show_path)
        else:
            fmt = ''
            if show_time:
                fmt += '[%(asctime)s] '
            fmt += '%(levelname)s - '
            if show_path:
                fmt += '%(filename)s:%(lineno)d - '
            fmt += '%(message)s'

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(fmt))

        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

    if log_file is not None:
        Path(log_file).parent.mkdir(exist_ok=True, parents=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

        root_logger.addHandler(file_handler)


def parse_dict(string: str) -> dict[str, list[str]] | None:
    """Parse a string in format 'key=value1,value2' into a dictionary.

    Args:
        string (str): String to parse in format 'key=value1,value2,value3'.

    Returns:
        Dictionary with single key mapping to list of values.
    """
    if string:
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
    if string:
        return [value.strip() for value in string.split(',')]
    else:
        return []


def parse_version(value: str) -> str:
    """Parse a version string in YYYYMMDD format.

    Args:
        value (str): Version string in YYYYMMDD format.

    Returns:
        Version string in YYYYMMDD format.

    Raises:
        argparse.ArgumentTypeError: If format is incorrect.
    """
    try:
        datetime.strptime(value, '%Y%m%d')
        return value
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


def parse_locations(value: str | list) -> list[str | Path]:
    """Parse and expand a location string as list of URL or Path objects.

    Args:
        value (str): Location string to parse.

    Returns:
        List of URL or Path objects.
    """
    if value:
        return [
            string.rstrip('/') if urlparse(string).scheme else Path(string).expanduser()
            for string in (value.split() if isinstance(value, str) else value)
        ]
    else:
        return []


def parse_filelist(filelist_file: str | Path | None) -> set[str]:
    """Parse a filelist file into a set of file paths.

    Args:
        filelist_file (str | Path | None): Path to file containing list of paths (one per line).
            Lines starting with '#' are treated as comments.

    Returns:
        List of file paths.
    """
    if filelist_file:
        with open(filelist_file) as f:
            return list({line for line in f.read().splitlines() if (line and not line.startswith('#'))})
    else:
        return []


def parse_parameters(value: str) -> Path:
    """Parse and expand a parameters string (a=b).

    Args:
        value (str): Parameter string to parse.

    Returns:
        Dict of the form {key: values}
    """
    if value:
        key, values_str = value.split('=')
        values = values_str.split(',')
        return {key: values}
    else:
        return {}


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

    env_prefix = 'ISIMIP_'

    def parse_args(self, *args, config_path=None) -> argparse.Namespace:
        return super().parse_args(*args, namespace=self.build_default_args(config_path))

    def get_defaults(self) -> dict:
        defaults = {}
        for action in self._actions:
            if not action.required and action.dest != 'help':
                defaults[action.dest] = action.default

        defaults.update(vars(self.build_default_args()))
        return defaults

    def read_global_config(self) -> dict:
        for config_file in self.config_files:
            config_path = Path(config_file).expanduser()
            if config_path.is_file():
                with open(config_path, 'rb') as fp:
                    data = tomllib.load(fp)
                    if self.prog in data:
                        return data[self.prog]
        return {}

    def read_local_config(self, config_path) -> dict:
        if config_path and config_path.is_file():
            with open(config_path, 'rb') as fp:
                return tomllib.load(fp)
        return {}

    def build_default_args(self, config_path=None) -> argparse.Namespace:
        # read config file(s)
        config = self.read_global_config()
        config.update(self.read_local_config(config_path))

        # init the default namespace
        default_args = argparse.Namespace()

        for action in self._actions:
            if action.dest not in ['config', 'help']:
                key = action.dest
                key_upper = key.upper()
                key_env = self.env_prefix + key_upper

                value = None

                if os.getenv(key_env):
                    # if the attribute is in the environment, take the value
                    value = os.getenv(key_env)
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.lower() == 'none':
                        value = None

                    # apply action type
                    if value and action.type is not None and value not in [True, False]:
                        try:
                            value = action.type(value)
                        except argparse.ArgumentTypeError as e:
                            raise ConfigError(f'argument "{key}": {e}') from e

                elif config and key in config:
                    # if the attribute is in the config file, take it from there
                    value = config.get(key)

                    # apply certain action types
                    if value and action.type in [parse_filelist, parse_locations, parse_path, parse_version]:
                        try:
                            value = action.type(value)
                        except argparse.ArgumentTypeError as e:
                            raise ConfigError(f'argument "{key}": {e}') from e

                if value is not None:
                    # check action.action
                    if action.const:
                        if value is True:
                            value = action.const
                        elif value is False:
                            value = None

                    # check action.choices
                    if action.choices and value not in action.choices:
                        raise ConfigError(f'argument "{key}": invalid choice "{value}" (choose from {action.choices})')

                    # check list
                    if action.type in (list, parse_list, parse_locations):
                        if not isinstance(value, list):
                            raise ConfigError(f'argument "{key}": needs to be a list')

                    # check dict
                    if action.type in (dict, parse_dict):
                        if not isinstance(value, list):
                            raise ConfigError(f'argument "{key}": needs to be a dict')

                    # add the key and value to the default_args
                    setattr(default_args, key, value)

        return default_args
