import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from isimip_utils.fetch import (
    fetch_definitions,
    fetch_json,
    fetch_pattern,
    fetch_schema,
    fetch_tree,
    find_json,
    load_json,
)

paths = [
    'ISIMIP3a/OutputData/agriculture/ACEA/gswp3-w5e5.json',
    'ISIMIP3a/OutputData/agriculture/ACEA.json',
    'ISIMIP3a/OutputData/agriculture.json'
]


def mock_side_effect(url, *args, **kwargs):
    mock_response = MagicMock()
    mock_path = Path(url.replace('https://protocol.isimip.org', 'testing/protocol/output'))

    if mock_path.exists():
        with mock_path.open() as fp:
            mock_response.status_code = 200
            mock_response.json.return_value = json.load(fp)
    else:
        mock_response.status_code = 404
        mock_response.json.return_value = None

    return mock_response


@pytest.mark.parametrize('path', paths)
def test_fetch_definitions(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=mock_side_effect):
        data = fetch_definitions(path)
        assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_definitions_local(path):
    data = fetch_definitions(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_pattern(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=mock_side_effect):
        data = fetch_pattern(path)
        assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_pattern_local(path):
    data = fetch_pattern(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_schema(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=mock_side_effect):
        data = fetch_schema(path)
        assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_schema_local(path):
    data = fetch_schema(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_tree(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=mock_side_effect):
        data = fetch_tree(path)
        assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_tree_local(path):
    data = fetch_tree(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_find_json_fetch(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=mock_side_effect):
        data = find_json('https://protocol.isimip.org', 'definitions', path)
        assert data is not None


@pytest.mark.parametrize('path', paths)
def test_find_json_load(path):
    data = find_json('testing/protocol', 'definitions', path)
    assert data is not None


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
