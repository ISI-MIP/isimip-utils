import pytest

from isimip_utils.exceptions import ValidationError
from isimip_utils.utils import (
    Singleton,
    cached_property,
    exclude_path,
    get_max_value,
    get_min_value,
    include_path,
    validate_lat,
    validate_lon,
)

paths = [
    'a/b/c',
    'a/b/d',
    'a/b/e'
]


def test_singleton():
    a = Singleton()
    a.egg = 'spam'

    b = Singleton()
    assert b.egg == 'spam'


def test_cached_property():

    class Test:

        def __init__(self):
            self.counter = 0

        @cached_property
        def egg(self):
            self.counter += 1
            return 'spam'

    t = Test()
    assert t.egg == 'spam'
    assert t.egg == 'spam'
    assert t.counter == 1


@pytest.mark.parametrize('lat', (-90.0, -45.5, 0, 45, 90))
def test_validate_lat(lat):
    validate_lat(lat)


@pytest.mark.parametrize('lat', (-91, 91, None, '', 'none'))
def test_validate_lat_error(lat):
    with pytest.raises(ValidationError):
        validate_lat(lat)


@pytest.mark.parametrize('lon', (-180.0, -45.5, 0, 45, 180))
def test_validate_lon(lon):
    validate_lon(lon)


@pytest.mark.parametrize('lon', (-181, 181, None, '', 'none'))
def test_validate_lon_error(lon):
    with pytest.raises(ValidationError):
        validate_lon(lon)


def test_exclude_path():
    assert exclude_path([], 'a/b/c') is False
    assert exclude_path(paths, 'a/b/c') is True
    assert exclude_path(paths, 'a/b/cc') is True
    assert exclude_path(paths, 'a/b/f') is False


def test_include_path():
    assert include_path([], 'a/b/c') is True
    assert include_path(paths, 'a/b/c') is True
    assert include_path(paths, 'a/b/cc') is True
    assert include_path(paths, 'a/b/f') is False


@pytest.mark.parametrize('values,result', [
    ([1, 2, 3], 1),
    ([None, 2, 3], 2),
    ([None, None, None], None),
    ([], None)
])
def test_get_min_value(values, result):
    assert get_min_value(values) == result


@pytest.mark.parametrize('values,result', [
    ([1, 2, 3], 3),
    ([1, 2, None], 2),
    ([None, None, None], None),
    ([], None)
])
def test_get_max_value(values, result):
    assert get_max_value(values) == result
