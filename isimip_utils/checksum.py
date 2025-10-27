"""Checksum computation utilities for file integrity verification."""
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


CHECKSUM_TYPE = 'sha512'


def get_checksum(abspath: str | Path, checksum_type: str = CHECKSUM_TYPE) -> str:
    """Compute the checksum of a file.

    Args:
        abspath (str | Path): Absolute path to the file to checksum.
        checksum_type (str): Type of checksum algorithm to use (default: 'sha512').

    Returns:
        The hexadecimal digest string of the file's checksum.
    """
    m = hashlib.new(checksum_type)
    with open(abspath, 'rb') as f:
        # read and update in blocks of 64K
        for block in iter(lambda: f.read(65536), b''):
            m.update(block)
    return m.hexdigest()


def get_checksum_type() -> str:
    """Get the default checksum type.

    Returns:
        The default checksum algorithm name (e.g., 'sha512').
    """
    return CHECKSUM_TYPE


def get_checksum_suffix() -> str:
    """Get the file suffix for checksum files.

    Returns:
        The checksum file extension (e.g., '.sha512').
    """
    return '.' + CHECKSUM_TYPE
