"""Functions to fetch files from urls or local paths."""
import json
import logging
import shutil
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


def fetch_json(url: str) -> Any | None:
    """Fetch JSON content from a URL.

    Args:
        location (str | Path): URL to fetch JSON from.

    Returns:
        Parsed JSON object, or None if request fails.
    """
    logger.debug('url = %s', url)

    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return None

    if response.status_code == 200:
        return response.json()


def fetch_file(url: str, target: None | str | Path = None) -> bool:
    """Download file from a URL.

    Args:
        location (str | Path): URL to download file from.
        target (str | Path): Target path, or None if the content should be returned.

    Returns:
        Target path if it was provided, the content otherwise, or None if the request fails.
    """
    logger.debug('url = %s', url)

    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return None

    if target is None:
        return response.content.decode()
    else:
        target.parent.mkdir(exist_ok=True, parents=True)
        if response.status_code == 200:
            with open(target, "wb") as fp:
                fp.write(response.content)
            return target


def load_json(path: str | Path) -> Any | None:
    """Load JSON content from a local path.

    Args:
        location (str | Path): URL to fetch JSON from.

    Returns:
        Parsed JSON object, or None if request fails.
    """
    logger.debug('path = %s', path)

    path = Path(path)
    if path.exists():
        return json.loads(open(path).read())


def load_file(path: str | Path, target: None | str | Path = None) -> bool:
    """Copy a file from a local path.

    Args:
        location (str | Path): URL to download file from.
        target (str | Path): Target path, or None if the content should be returned.

    Returns:
        Target path if it was provided, the content otherwise, or None if the request fails.
    """
    logger.debug('path = %s', path)

    path = Path(path)
    if path.is_file():
        if target is None:
            return path.read_text()
        else:
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(path, target)
            return target
