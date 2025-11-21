import pytest

from isimip_utils.exceptions import ValidationError
from isimip_utils.utils import (
    Singleton,
    cached_property,
    copy_placeholders,
    exclude_path,
    get_permutations,
    get_placeholders,
    include_path,
    join_parameters,
    update_year,
    validate_lat,
    validate_lon,
)

paths = [
    'a/b/c',
    'a/b/d',
    'a/b/e'
]

parameters = {
    'model': ['model_a', 'model_b'],
    'variable': ['x', 'y', 'z']
}


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


def test_get_permutations():
    assert get_permutations(parameters) == (
        ('model_a', 'x'),
        ('model_a', 'y'),
        ('model_a', 'z'),
        ('model_b', 'x'),
        ('model_b', 'y'),
        ('model_b', 'z')
    )


def test_get_placeholders():
    assert get_placeholders(parameters, ('model_a', 'x')) == {
        'model': 'model_a',
        'variable': 'x'
    }


def test_join_parameters():
    assert join_parameters(parameters) == {
        'model': 'model_a+model_b',
        'variable': 'x+y+z'
    }


def test_join_parameters_max_count():
    assert join_parameters(parameters, 2) == {
        'model': 'model_a+model_b',
        'variable': 'various'
    }


def test_join_parameters_max_count_label():
    assert join_parameters(parameters, 2, 'label') == {
        'model': 'model_a+model_b',
        'variable': 'label'
    }


def test_copy_placeholders():
    assert copy_placeholders({'foo': 'bar'}, {'egg': 'spam'}) == {
        'foo': 'bar',
        'egg': 'spam'
    }


def test_update_year():
    placeholders = {'year': 2000}

    update_year(placeholders, 'year', 2001, '<')
    assert placeholders == {'year': 2000}

    update_year(placeholders, 'year', 2001, '>')
    assert placeholders == {'year': 2001}

    update_year(placeholders, 'year', 2000, '<')
    assert placeholders == {'year': 2000}
