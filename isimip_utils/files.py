"""Functions to find files for specific datasets."""
import logging
import re
from collections.abc import Iterable
from pathlib import Path

logger = logging.getLogger(__name__)


def find_files(base_path: str | Path, file_iter: Iterable[Path],
               pattern: str = r'_(?P<start_year>\d{4})_(?P<end_year>\d{4})?\.nc\d*$') -> tuple[list[tuple], int, int]:
    """Find files for a given (dataset) path, matching a regex pattern for start and end year.

    Args:
        base_path (str | Path): Base path for file discovery.
        file_iter (Iterable[Path]): Iterator over file paths to search through.
        pattern (str): Regular expression for start and end year matching.

    Returns:
        Tuple containing (a) the List of tuples containing the path and the start and end years for each file,
        (b) the lowest start year, and (c) the highest end year.
    """
    files = []

    for file_path in sorted(file_iter):
        match = re.search(pattern, str(file_path), re.IGNORECASE)
        if match:
            try:
                start_year = int(match.group('start_year'))
            except TypeError:
                start_year = None

            try:
                end_year = int(match.group('end_year'))
            except TypeError:
                end_year = None

            files.append((file_path, start_year, end_year))

    return files
