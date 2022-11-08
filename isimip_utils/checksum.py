import hashlib
import logging

logger = logging.getLogger(__name__)


CHECKSUM_TYPE = 'sha512'


def get_checksum(abspath, checksum_type=CHECKSUM_TYPE):
    m = hashlib.new(checksum_type)
    with open(abspath, 'rb') as f:
        # read and update in blocks of 64K
        for block in iter(lambda: f.read(65536), b''):
            m.update(block)
    return m.hexdigest()


def get_checksum_type():
    return CHECKSUM_TYPE


def get_checksum_suffix():
    return '.' + CHECKSUM_TYPE
