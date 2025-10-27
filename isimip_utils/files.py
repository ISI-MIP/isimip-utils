"""File search utilities for ISIMIP tools."""
import re
from pathlib import Path


def find_files(base_path: Path, pattern: str) -> list[dict]:
    """Find files matching a regex pattern in a directory tree.

    Args:
        base_path (Path): Base directory to search in.
        pattern (str): Regular expression pattern to match against file paths.

    Returns:
        List of dictionaries containing 'path' and any named groups from the regex match.
    """
    files = []
    for path in sorted(base_path.rglob("*")):
        match = re.search(str(pattern), str(path), re.IGNORECASE)
        if match:
            files.append(dict(path=path, **match.groupdict()))

    return files
