from unittest.mock import patch

from isimip_utils.fetch import (
    fetch_json,
    load_json,
)

from .helper import mock_side_effect

paths = [
    'ISIMIP3a/OutputData/agriculture/ACEA/gswp3-w5e5.json',
    'ISIMIP3a/OutputData/agriculture/ACEA.json',
    'ISIMIP3a/OutputData/agriculture.json'
]

def test_fetch_json():
    with patch('isimip_utils.fetch.requests.get', side_effect=mock_side_effect):
        data = fetch_json("https://protocol.isimip.org/definitions/ISIMIP3a/OutputData/agriculture.json")
        assert data is not None


def test_fetch_json_not_found():
    with patch('isimip_utils.fetch.requests.get', side_effect=mock_side_effect):
        data = fetch_json("https://protocol.isimip.org/definitions/ISIMIP3a/OutputData/agriculture/ACEA.json")
        assert data is None


def test_load_json():
    data =  load_json('testing/protocol/output/definitions/ISIMIP3a/OutputData/agriculture.json')
    assert data is not None


def test_load_json_not_found():
    data = load_json('testing/protocol/output/definitions/ISIMIP3a/OutputData/agriculture/ACEA.json')
    assert data is None
