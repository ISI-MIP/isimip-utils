import logging
import re

from pathlib import Path

from .exceptions import DidNotMatch

logger = logging.getLogger(__name__)

year_pattern = re.compile(r'^\d{4}$')


def match_dataset_path(pattern, dataset_path):
    return match_path(pattern, dataset_path, filename_pattern_key='dataset')


def match_file_path(pattern, file_path):
    return match_path(pattern, file_path)


def match_path(pattern, path, dirname_pattern_key='path', filename_pattern_key='file'):
    dirname_pattern = pattern[dirname_pattern_key]
    filename_pattern = pattern[filename_pattern_key]

    # match the dirname and the filename
    dirname_path, dirname_specifiers = match_string(dirname_pattern, path.parent.as_posix())
    filename_path, filename_specifiers = match_string(filename_pattern, path.name)

    path = dirname_path / filename_path

    # assert that any value in dirname_specifiers at least starts with
    # its corresponding value (same key) in filename_specifiers
    # e.g. 'ewe' and 'ewe_north-sea'
    for key, value in filename_specifiers.items():
        if key in dirname_specifiers:
            f, d = filename_specifiers[key], dirname_specifiers[key]

            if not d.lower().startswith(f.lower()):
                raise DidNotMatch('dirname_specifier "{}" does not match filename_specifier "{}" in {}'.format(d, f, path))

    # merge filename_specifiers and dirname_specifiers
    specifiers = {**dirname_specifiers, **filename_specifiers}

    # apply specifiers_map if it exists
    if pattern['specifiers_map']:
        for key, value in specifiers.items():
            if value in pattern['specifiers_map']:
                specifiers[key] = pattern['specifiers_map'][value]

    # add fixed specifiers
    specifiers.update(pattern['specifiers'])

    return path, specifiers


def match_dataset(pattern, path):
    return match_string(pattern['dataset'], path.name)


def match_file(pattern, path):
    return match_string(pattern['file'], path.name)


def match_string(pattern, string):
    logger.debug(pattern.pattern)
    logger.debug(string)

    # try to match the string
    match = pattern.search(string)
    if match:
        specifiers = {}
        for key, value in match.groupdict().items():
            if value is not None:
                if year_pattern.search(value):
                    specifiers[key] = int(value)
                else:
                    specifiers[key] = value

        return Path(match.group(0)), specifiers
    else:
        raise DidNotMatch('No match for {} ("{}")'.format(string, pattern.pattern))
