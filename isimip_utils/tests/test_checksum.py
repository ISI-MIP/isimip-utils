from isimip_utils.checksum import get_checksum, get_checksum_suffix, get_checksum_type
from isimip_utils.tests import constants


def test_get_checksum():
    file_path = constants.DATASETS_PATH / constants.LANDSEAMASK_PATH
    checksum = get_checksum(file_path)
    assert checksum == '30f34d0720b8a6b670d0c093d488a3cd564e232a94d7ebafef99c1d7c18cec5d127fbc663f6378b4b99f9434fa10f71e8413b533c5cc5314d149ab9e2f7cca98'  # noqa: E501


def test_get_checksum_type():
    assert get_checksum_type() == 'sha512'


def test_get_checksum_suffix():
    assert get_checksum_suffix() == '.sha512'
