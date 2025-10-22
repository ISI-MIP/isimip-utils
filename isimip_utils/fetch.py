import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

from isimip_utils.exceptions import NotFound

logger = logging.getLogger(__name__)

PROTOCOL_LOCATIONS = [
    'https://protocol.isimip.org',
    'https://protocol2.isimip.org',
]

def fetch_definitions(path, protocol_locations=PROTOCOL_LOCATIONS):
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        for definitions_path, definitions_json in find_json(protocol_location, 'definitions', path):
            if definitions_json:
                logger.debug('definitions_path = %s', definitions_path)
                logger.debug('definitions_json = %s', definitions_json)

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

    raise NotFound(f'no definitions found for {path}')


def fetch_pattern(path, protocol_locations=PROTOCOL_LOCATIONS):
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        for pattern_path, pattern_json in find_json(protocol_location, 'pattern', path):
            if pattern_json:
                logger.debug('pattern_path = %s', pattern_path)
                logger.debug('pattern_json = %s', pattern_json)

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

    raise NotFound(f'no pattern found for {path}')


def fetch_schema(path, protocol_locations=PROTOCOL_LOCATIONS):
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        for schema_path, schema_json in find_json(protocol_location, 'schema', path):
            if schema_json:
                logger.debug('schema_path = %s', schema_path)
                logger.debug('schema_json = %s', schema_json)
                return schema_json

    raise NotFound(f'no schema found for {path}')


def fetch_tree(path, protocol_locations=PROTOCOL_LOCATIONS):
    if isinstance(protocol_locations, str):
        protocol_locations = [protocol_locations]

    for protocol_location in protocol_locations:
        for tree_path, tree_json in find_json(protocol_location, 'tree', path):
            if tree_json:
                logger.debug('tree_path = %s', tree_path)
                logger.debug('tree_json = %s', tree_json)
                return tree_json

    raise NotFound(f'no tree found for {path}')


def find_json(protocol_location, sub_location, path):
    path_components = Path(path).parts
    for i in range(len(path_components), 0, -1):
        current_path = Path(os.sep.join(path_components[:i+1])).with_suffix('.json')

        if urlparse(protocol_location).scheme:
            yield current_path, fetch_json(f'{protocol_location}/{sub_location}/{current_path}')
        else:
            yield current_path, load_json(Path(protocol_location) / 'output' / sub_location / current_path)


def fetch_json(location):
    logger.debug('location = %s', location)

    try:
        response = requests.get(location)
    except requests.exceptions.ConnectionError:
        return None

    if response.status_code == 200:
        return response.json()


def load_json(path):
    path = Path(path).expanduser()

    logger.debug('path = %s', path)

    if path.exists():
        return json.loads(open(path).read())
