from datetime import datetime
from pathlib import Path

import pytest

import numpy as np
from netCDF4 import Dataset

from isimip_utils.netcdf import (
    convert_attribute,
    get_data_model,
    get_dimensions,
    get_global_attributes,
    get_index,
    get_variables,
    init_dataset,
    open_dataset,
    open_dataset_read,
    open_dataset_write,
    update_global_attributes,
    value2string,
)
from isimip_utils.tests import constants


def test_open_dataset():
    dataset = open_dataset(constants.DATASETS_PATH / constants.LANDSEAMASK_PATH)
    assert isinstance(dataset, Dataset)


def test_open_dataset_read():
    dataset = open_dataset_read(constants.DATASETS_PATH / constants.LANDSEAMASK_PATH)
    assert isinstance(dataset, Dataset)


def test_open_dataset_write():
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    dataset = open_dataset_write(test_path)
    assert isinstance(dataset, Dataset)


def test_init_dataset():
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    dataset = init_dataset(test_path)
    assert isinstance(dataset, Dataset)


@pytest.mark.parametrize('point,result', [
    ((89.75, -179.75), (0, 0)),
    ((89.75, -179.25), (1, 0)),
    ((89.25, -179.75), (0, 1)),
    ((52.395833, 13.061389), (386, 75))
])
def test_get_index(point, result):
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    lat, lon = point
    dataset = init_dataset(test_path, overwrite=True)
    assert get_index(dataset, lat, lon) == result


def test_get_data_model():
    dataset = Dataset(constants.DATASETS_PATH / constants.LANDSEAMASK_PATH)
    data_model = get_data_model(dataset)
    assert data_model == 'NETCDF4_CLASSIC'


def test_get_dimensions():
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    dataset = init_dataset(test_path, overwrite=True)
    dimensions = get_dimensions(dataset)
    assert list(dimensions.items()) == [
        ('lon', 720),
        ('lat', 360)
    ]


def test_get_variables():
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    dataset = init_dataset(test_path, overwrite=True)
    variables = get_variables(dataset)
    assert [(variable_name, variable['standard_name']) for variable_name, variable in variables.items()] == [
        ('lon', 'longitude'),
        ('lat', 'latitude')
    ]


def test_get_global_attributes():
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    dataset = init_dataset(test_path, overwrite=True, attrs={
        'global': {
            'egg': 'spam',
            'x': np.float32(3.0)
        }
    })
    global_attrs = get_global_attributes(dataset)

    assert global_attrs['egg'] == 'spam'
    assert global_attrs['x'] == np.float32(3.0)


@pytest.mark.parametrize('value,return_value', [
    (np.float32(3.0), 3.0),
    (np.int32(42), 42),
    ([1, 2, 3], [1, 2, 3]),
    (np.array([1, 2, 3]), [1, 2, 3]),
    ([np.float32(1.0), np.int32(2)], [1.0, 2])
])
def test_convert_attribute(value, return_value):
    assert convert_attribute(value) == return_value


def test_update_global_attributes_set():
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    dataset = init_dataset(test_path, overwrite=True)
    update_global_attributes(dataset, set_attributes={
        'egg': 'spam'
    })

    assert dataset.egg == 'spam'


def test_update_global_attributes_delete():
    test_path = Path('testing/output') / 'test.nc'
    test_path.parent.mkdir(exist_ok=True)
    test_path.unlink(missing_ok=True)

    dataset = init_dataset(test_path, overwrite=True, attrs={
        'global': {
            'egg': 'spam'
        }
    })
    update_global_attributes(dataset, delete_attributes=['egg'])

    with pytest.raises(AttributeError):
        assert dataset.egg


@pytest.mark.parametrize('value,string', [
    (datetime(2023, 1, 1, 12, 0, 0), '2023-01-01T12:00:00Z'),
    (123, '123'),
    ('test', 'test'),
    (None, 'None')
])
def test_value2string(value, string):
    assert value2string(value) == string
