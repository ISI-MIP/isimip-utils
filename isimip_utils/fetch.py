"""Functions to fetch files from machine-actionable ISIMIP protocols."""
import json
import logging
import os
import re
from collections.abc import Generator
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from isimip_utils.exceptions import NotFound

logger = logging.getLogger(__name__)

PROTOCOL_LOCATIONS = [
    'https://protocol.isimip.org',
    'https://protocol2.isimip.org',
]


def fetch_definitions(path: str | Path, protocol_locations: str | list[str] = PROTOCOL_LOCATIONS) -> dict[str, Any]:
    """Fetch definitions from ISIMIP protocol locations.

    Args:
        path (str | Path): Path to search for definitions.
        protocol_locations (str | list[str]): List of protocol locations to search (default: https://protocol.isimip.org).

    Returns:
        Dictionary of definitions with specifiers as keys.

    Raises:
        NotFound: If no definitions are found for the given path.
    """
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        definitions_json = find_json(protocol_location, 'definitions', path)
        if definitions_json:
            definitions = {}
            for definition_name, definition in definitions_json.items():
                # convert the definitions to dicts if they are lists
                if isinstance(definition, list):
                    definitions[definition_name] = {
                        row['specifier']: row for row in definition
                    }
                else:
                    definitions[definition_name] = definition

            logger.debug('definitions = %s', definitions)
            return definitions

    raise NotFound(f'No definitions found for {path}.')


def fetch_pattern(path: str | Path, protocol_locations: str | list[str] = PROTOCOL_LOCATIONS) -> dict[str, Any]:
    """Fetch pattern definitions from ISIMIP protocol locations.

    Args:
        path (str | Path): Path to search for patterns.
        protocol_locations (str | list[str]): List of protocol locations to search (default: https://protocol.isimip.org).

    Returns:
        Dictionary containing compiled regex patterns for 'path', 'file', 'dataset',
        and lists of 'suffix', 'specifiers', and 'specifiers_map'.

    Raises:
        NotFound: If no pattern is found for the given path.
    """
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        pattern_json = find_json(protocol_location, 'pattern', path)
        if pattern_json:
            if not all([
                isinstance(pattern_json['path'], str),
                isinstance(pattern_json['file'], str),
                isinstance(pattern_json['dataset'], str),
                isinstance(pattern_json['suffix'], list)
            ]):
                break

            pattern = {
                'path': re.compile(pattern_json['path']),
                'file': re.compile(pattern_json['file']),
                'dataset': re.compile(pattern_json['dataset']),
                'suffix': pattern_json['suffix'],
                'specifiers': pattern_json.get('specifiers', []),
                'specifiers_map': pattern_json.get('specifiers_map', {})
            }

            logger.debug('pattern = %s', pattern)

            return pattern

    raise NotFound(f'No pattern found for {path}.')


def fetch_schema(path: str | Path, protocol_locations: str | list[str] = PROTOCOL_LOCATIONS) -> Any:
    """Fetch schema from ISIMIP protocol locations.

    Args:
        path (str | Path): Path to search for schema.
        protocol_locations (str | list[str]): List of protocol locations to search (default: https://protocol.isimip.org).

    Returns:
        Schema JSON object.

    Raises:
        NotFound: If no schema is found for the given path.
    """
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        schema_json = find_json(protocol_location, 'schema', path)
        if schema_json:
            return schema_json

    raise NotFound(f'No schema found for {path}.')


def fetch_tree(path: str | Path, protocol_locations: str | list[str] = PROTOCOL_LOCATIONS) -> Any:
    """Fetch tree structure from ISIMIP protocol locations.

    Args:
        path (str | Path): Path to search for tree structure.
        protocol_locations (str | list[str]): List of protocol locations to search (default: https://protocol.isimip.org).

    Returns:
        Tree JSON object.

    Raises:
        NotFound: If no tree is found for the given path.
    """
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        tree_json = find_json(protocol_location, 'tree', path)
        if tree_json:
            return tree_json

    raise NotFound(f'No tree found for {path}.')


def fetch_resource(resource_location: str | Path) -> dict:
    if urlparse(resource_location).scheme:
        return fetch_json(resource_location)
    else:
        return load_json(resource_location)

    raise NotFound(f'No resource found at {resource_location}.')


def find_json(protocol_location: str, sub_location: str, path: str | Path) -> Generator[tuple[Path, Any], None, None]:
    """Find JSON files in protocol locations by traversing path components.

    Args:
        protocol_location (str): Base protocol location URL or path.
        sub_location (str): Subdirectory within protocol location (e.g., 'definitions', 'pattern').
        path (str | Path): Path to search for JSON files.

    Returns:
        The JSON response from the first matching path.
    """
    path_components = Path(path).parts
    for i in range(len(path_components), 0, -1):
        current_path = Path(os.sep.join(path_components[:i+1])).with_suffix('.json')

        if urlparse(protocol_location).scheme:
            data = fetch_json(f'{protocol_location}/{sub_location}/{current_path}')
        else:
            data = load_json(Path(protocol_location) / 'output' / sub_location / current_path)

        logger.debug('path = %s', current_path)
        logger.debug('data = %s', data)

        if data is not None:
            return data


def fetch_json(location: str) -> Any | None:
    """Fetch JSON content from a URL.

    Args:
        location (str): URL to fetch JSON from.

    Returns:
        Parsed JSON object, or None if request fails or status is not 200.
    """
    logger.debug('location = %s', location)

    try:
        response = requests.get(location)
    except requests.exceptions.ConnectionError:
        return None

    if response.status_code == 200:
        return response.json()


def load_json(path: str | Path) -> Any | None:
    """Load JSON content from a local file.

    Args:
        path (str | Path): Path to the JSON file.

    Returns:
        Parsed JSON object, or None if file doesn't exist.
    """
    path = Path(path).expanduser()

    logger.debug('path = %s', path)

    if path.exists():
        return json.loads(open(path).read())
