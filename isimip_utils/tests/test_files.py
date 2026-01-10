from pathlib import Path

from isimip_utils.files import find_files
from isimip_utils.tests import constants


def test_find_files():
    file_path = Path(constants.YIELD_PATH)
    fake_path = file_path.with_stem(file_path.stem + '_a')
    files = [
        file_path.name,
        fake_path.name
    ]

    result = find_files(files)
    assert len(result)
    assert result == [
        (file_path.name, 1901, 2016)
    ]


def test_find_files_with_pattern():
    file_path = Path(constants.YIELD_PATH)
    fake_path = file_path.with_stem(file_path.stem + '_a')
    none_path = file_path.with_stem(file_path.stem.replace('_1901_2016', ''))
    files = [
        file_path.name,
        fake_path.name,
        none_path.name,
    ]

    pattern = r'(_(?P<start_year>\d{4}))?(_(?P<end_year>\d{4}))?(_\w+)?\.nc\d*$'

    result = find_files(files, pattern=pattern)
    assert len(result)
    assert result == [
        (none_path.name, None, None),  # result is sorted
        (file_path.name, 1901, 2016),
        (fake_path.name, 1901, 2016),
    ]
