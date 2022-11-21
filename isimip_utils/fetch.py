import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def fetch_definitions(bases, path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        definitions_path = Path('definitions').joinpath(os.sep.join(path_components[:i+1])).with_suffix('.json')
        definitions_json = fetch_json(bases, definitions_path)

        if definitions_json:
            logger.info('definitions_path = %s', definitions_path)
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


def fetch_pattern(bases, path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        pattern_path = Path('pattern').joinpath(os.sep.join(path_components[:i+1]) + '.json')
        pattern_json = fetch_json(bases, pattern_path)

        if pattern_json:
            logger.info('pattern_path = %s', pattern_path)
            logger.debug('pattern_json = %s', pattern_json)

            assert isinstance(pattern_json['path'], str)
            assert isinstance(pattern_json['file'], str)
            assert isinstance(pattern_json['dataset'], str)
            assert isinstance(pattern_json['suffix'], list)

            pattern = {
                'path': re.compile(pattern_json['path']),
                'file': re.compile(pattern_json['file']),
                'dataset': re.compile(pattern_json['dataset']),
                'suffix': pattern_json['suffix'],
                'specifiers': pattern_json['specifiers'],
                'specifiers_map': pattern_json['specifiers_map']
            }

            logger.debug('pattern = %s', pattern)

            return pattern


def fetch_schema(bases, path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        schema_path = Path('schema').joinpath(os.sep.join(path_components[:i+1])).with_suffix('.json')
        schema_json = fetch_json(bases, schema_path)

        if schema_json:
            logger.info('schema_path = %s', schema_path)
            logger.debug('schema_json = %s', schema_json)
            return schema_json


def fetch_tree(bases, path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        tree_path = Path('tree').joinpath(os.sep.join(path_components[:i+1])).with_suffix('.json')
        tree_json = fetch_json(bases, tree_path)

        if tree_json:
            logger.info('tree_path = %s', tree_path)
            logger.debug('tree_json = %s', tree_json)
            return tree_json


def fetch_resource(location):
    return fetch_json([location])


def fetch_json(bases, path=None):
    for base in bases:
        if urlparse(base).scheme:
            if path is not None:
                location = base.rstrip('/') + '/' + path.as_posix()
            else:
                location = base.rstrip('/')

            logger.debug('json_url = %s', location)
            response = requests.get(location)

            if response.status_code == 200:
                return response.json()

        else:
            location = Path(base).expanduser() / 'output'
            if path is not None:
                location /= path

            logger.debug('json_path = %s', location)

            if location.exists():
                return json.loads(open(location).read())
