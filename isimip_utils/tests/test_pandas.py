import pytest

from isimip_utils.pandas import (
    compute_average,
    create_label,
    get_coord_axes,
    get_coord_labels,
    get_coords,
    get_data_var_labels,
    get_data_vars,
    get_first_coord,
    get_first_coord_axis,
    get_first_coord_label,
    get_first_data_var,
    get_first_data_var_label,
    group_by_day,
    group_by_month,
    normalize,
)
from isimip_utils.tests import constants
from isimip_utils.xarray import open_dataset, to_dataframe

extractions = {
    'bbox': constants.TAS_PATH.replace('_global_', '_select-bbox-cdo_'),
    'point': constants.TAS_PATH.replace('_global_', '_select-point-cdo_')
}

@pytest.mark.parametrize('extraction,result', [
    ('bbox', ('lon', 'lat', 'time')),
    ('point', ('time', ))
])
def test_get_coords(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_coords(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('point', 'time')
])
def test_get_first_coord(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_first_coord(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('bbox', ('Longitude [degrees_east]', 'Latitude [degrees_north]', 'Time')),
    ('point', ('Time', ))
])
def test_get_coord_labels(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_coord_labels(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('point', 'Time')
])
def test_get_first_coord_label(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_first_coord_label(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('bbox', ('X', 'Y', 'T')),
    ('point', ('T', ))
])
def test_get_coord_axes(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_coord_axes(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('point', 'T')
])
def test_get_first_coord_axis(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_first_coord_axis(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('bbox', ('tas', )),
    ('point', ('tas', ))
])
def test_get_data_vars(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_data_vars(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('point', 'tas')
])
def test_get_first_data_var(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_first_data_var(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('bbox', ('Near-Surface Air Temperature [K]', )),
    ('point', ('Near-Surface Air Temperature [K]', ))
])
def test_get_data_var_labels(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_data_var_labels(df) == result


@pytest.mark.parametrize('extraction,result', [
    ('point', 'Near-Surface Air Temperature [K]')
])
def test_get_first_data_var_label(extraction, result):
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions[extraction]) as ds:
        df = to_dataframe(ds)
        assert get_first_data_var_label(df) == result


def test_compute_average():
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions['point']) as ds:
        df = to_dataframe(ds)
        df = compute_average(df, 'tas')

        assert df['lower'].between(270, 280).all()
        assert df['mean'].between(280, 290).all()
        assert df['upper'].between(290, 300).all()


def test_group_by_day():
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions['point']) as ds:
        df = to_dataframe(ds)
        df = group_by_day(df, 'tas')

        assert len(df) == 365
        assert df['tas'].between(260, 305).all()


def test_group_by_month():
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions['point']) as ds:
        df = to_dataframe(ds)
        df = group_by_month(df, 'tas')

        assert len(df) == 12
        assert df['tas'].between(260, 300).all()


def test_normalize():
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions['point']) as ds:
        df = to_dataframe(ds)
        df = normalize(df, 'tas')

        assert df['tas'].between(-4, 4).all()


def test_create_label():
    with open_dataset(constants.EXTRACTIONS_PATH  / extractions['point']) as ds:
        df = to_dataframe(ds)
        df = create_label(df, ['x', 'y', 'z'])

        assert (df['label'] == 'x y z').all()
