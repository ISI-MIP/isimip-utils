import logging
from pathlib import Path

from dotenv import load_dotenv
from rich.logging import RichHandler


def setup_env():
    load_dotenv(Path().cwd() / '.env')


def setup_logs(log_level='WARN', log_file=None):
    log_level = log_level.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    rich_handler = RichHandler()
    rich_handler.setLevel(log_level)

    root_logger.addHandler(RichHandler())

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))

        root_logger.addHandler(file_handler)
