from unittest.mock import patch

from isimip_utils.fetch import fetch_file, fetch_json, load_file, load_json
from isimip_utils.tests import constants, helper

paths = [
    'ISIMIP3a/OutputData/agriculture/ACEA/gswp3-w5e5.json',
    'ISIMIP3a/OutputData/agriculture/ACEA.json',
    'ISIMIP3a/OutputData/agriculture.json'
]


def test_fetch_json():
    with patch('isimip_utils.fetch.requests.get', side_effect=helper.mock_json):
        data = fetch_json("https://protocol.isimip.org/definitions/ISIMIP3a/OutputData/agriculture.json")
        assert data is not None


def test_fetch_json_not_found():
    with patch('isimip_utils.fetch.requests.get', side_effect=helper.mock_json):
        data = fetch_json("https://protocol.isimip.org/definitions/ISIMIP3a/OutputData/agriculture/ACEA.json")
        assert data is None


def test_fetch_file():
    with patch('isimip_utils.fetch.requests.get', side_effect=helper.mock_content):
        output_path = constants.OUTPUT_PATH / 'test.json'
        output_path.unlink(missing_ok=True)

        fetch_file("https://protocol.isimip.org/definitions/ISIMIP3a/OutputData/agriculture.json", output_path)
        assert output_path.is_file()


def test_load_json():
    data =  load_json('testing/protocol/output/definitions/ISIMIP3a/OutputData/agriculture.json')
    assert data is not None


def test_load_json_not_found():
    data = load_json('testing/protocol/output/definitions/ISIMIP3a/OutputData/agriculture/ACEA.json')
    assert data is None


def test_load_file():
    output_path = constants.OUTPUT_PATH / 'test.json'
    output_path.unlink(missing_ok=True)

    load_file('testing/protocol/output/definitions/ISIMIP3a/OutputData/agriculture.json', output_path)
    assert output_path.is_file()
