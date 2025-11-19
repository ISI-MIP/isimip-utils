"""Functions to match file names and extract ISIMIP specifiers."""
import logging
import re
from collections.abc import Iterable
from pathlib import Path

from .exceptions import DidNotMatch

logger = logging.getLogger(__name__)

year_pattern = re.compile(r'^\d{4}$')


def match_dataset_path(pattern: dict, dataset_path: Path) -> tuple[Path, dict]:
    """Match a dataset path against a pattern.

    Args:
        pattern (dict): Pattern dictionary containing regex patterns.
        dataset_path (Path): Path to the dataset to match.

    Returns:
        Tuple of (matched_path, specifiers_dict).

    Raises:
        DidNotMatch: If the path doesn't match the pattern.
    """
    return match_path(pattern, dataset_path, filename_pattern_key='dataset')


def match_file_path(pattern: dict, file_path: Path) -> tuple[Path, dict]:
    """Match a file path against a pattern.

    Args:
        pattern (dict): Pattern dictionary containing regex patterns.
        file_path (Path): Path to the file to match.

    Returns:
        Tuple of (matched_path, specifiers_dict).

    Raises:
        DidNotMatch: If the path doesn't match the pattern.
    """
    return match_path(pattern, file_path)


def match_path(pattern: dict, path: Path, dirname_pattern_key: str = 'path',
               filename_pattern_key: str = 'file') -> tuple[Path, dict]:
    """Match both directory and filename components of a path against patterns.

    Args:
        pattern (dict): Pattern dictionary containing regex patterns and specifiers.
        path (Path): Path object to match.
        dirname_pattern_key (str): Key in pattern dict for directory pattern (default: 'path').
        filename_pattern_key (str): Key in pattern dict for filename pattern (default: 'file').

    Returns:
        Tuple of (matched_path, specifiers_dict) containing extracted specifiers.

    Raises:
        DidNotMatch: If dirname and filename specifiers conflict.
    """
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
                raise DidNotMatch(f'dirname_specifier "{d}" does not match filename_specifier "{f}" in {path}')

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


def match_dataset(pattern: dict, path: Path) -> tuple[Path, dict]:
    """Match a dataset name against a pattern.

    Args:
        pattern (dict): Pattern dictionary containing regex patterns.
        path (Path): Path object with dataset name.

    Returns:
        Tuple of (matched_path, specifiers_dict).

    Raises:
        DidNotMatch: If the dataset name doesn't match the pattern.
    """
    return match_string(pattern['dataset'], path.name)


def match_file(pattern: dict, path: Path) -> tuple[Path, dict]:
    """Match a file name against a pattern.

    Args:
        pattern (dict): Pattern dictionary containing regex patterns.
        path (Path): Path object with file name.

    Returns:
        Tuple of (matched_path, specifiers_dict).

    Raises:
        DidNotMatch: If the file name doesn't match the pattern.
    """
    return match_string(pattern['file'], path.name)


def match_string(pattern: re.Pattern, string: str) -> tuple[Path, dict]:
    """Match a string against a regex pattern and extract specifiers.

    Args:
        pattern (re.Pattern): Compiled regex pattern with named groups.
        string (str): String to match against the pattern.

    Returns:
        Tuple of (Path of matched portion, specifiers_dict).
        Year values (4-digit numbers) are converted to integers.

    Raises:
        DidNotMatch: If the string doesn't match the pattern.
    """
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
        raise DidNotMatch(f'No match for {string} ("{pattern.pattern}")')


def find_files(pattern: re.Pattern, file_iter: Iterable[Path]) -> list[dict]:
    """Find files matching a regex pattern from an iterator.

    Args:
        pattern (re.Pattern): Compiled regular expression pattern to match against file paths.
        file_iter (Iterable[Path]): Iterator over file paths to search through.

    Returns:
        List of dictionaries containing 'path' and any named groups from the regex match.
    """
    files = []
    for path in sorted(file_iter):
        try:
            files.append(match_string(pattern, path))
        except DidNotMatch:
            pass

    return files
