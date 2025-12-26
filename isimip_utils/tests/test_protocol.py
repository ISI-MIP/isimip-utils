from unittest.mock import patch

import pytest

from isimip_utils.protocol import (
    fetch_definitions,
    fetch_pattern,
    fetch_schema,
    fetch_tree,
    find_json,
)
from isimip_utils.tests import helper

paths = [
    'ISIMIP3a/OutputData/agriculture/ACEA/gswp3-w5e5.json',
    'ISIMIP3a/OutputData/agriculture/ACEA.json',
    'ISIMIP3a/OutputData/agriculture.json'
]


@pytest.mark.parametrize('path', paths)
def test_fetch_definitions_local(path):
    data = fetch_definitions(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_pattern(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=helper.mock_json):
        data = fetch_pattern(path)
        assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_pattern_local(path):
    data = fetch_pattern(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_schema(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=helper.mock_json):
        data = fetch_schema(path)
        assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_schema_local(path):
    data = fetch_schema(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_tree(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=helper.mock_json):
        data = fetch_tree(path)
        assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_fetch_tree_local(path):
    data = fetch_tree(path, 'testing/protocol')
    assert data and isinstance(data, dict)


@pytest.mark.parametrize('path', paths)
def test_find_json_fetch(path):
    with patch('isimip_utils.fetch.requests.get', side_effect=helper.mock_json):
        data = find_json('https://protocol.isimip.org', 'definitions', path)
        assert data is not None


@pytest.mark.parametrize('path', paths)
def test_find_json_load(path):
    data = find_json('testing/protocol', 'definitions', path)
    assert data is not None
