from pathlib import Path

import geopandas as gpd
import numpy as np
import xarray as xr
from shapely.geometry import box

from isimip_utils.netcdf import open_dataset_read
from isimip_utils.xarray import (
    add_fill_value_to_attrs,
    create_mask,
    get_attrs,
    init_dataset,
    load_dataset,
    open_dataset,
    order_variables,
    set_attrs,
    set_fill_value_to_nan,
    set_nan_to_fill_value,
    to_dataframe,
    write_dataset,
)

datasets_path = Path('testing/datasets')

dataset_path = datasets_path / "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc"  # noqa: E501

landseamask_path = datasets_path / 'ISIMIP3a/InputData/geo_conditions/landseamask/landseamask.nc'

test_path = Path('testing/output') / 'test.nc'
test_path.parent.mkdir(exist_ok=True)


def test_init_dataset():
    ds = init_dataset()

    assert isinstance(ds, xr.Dataset)
    assert ds.sizes['lon'] == 720
    assert ds.sizes['lat'] == 360


def test_init_dataset_args():
    lon_size, lat_size, time_size = 180, 90, 10

    time = np.arange(time_size, dtype=np.float64)
    var = np.random.rand(time_size, lat_size, lon_size).astype(np.float64)

    time_units = 'days since 2000-01-01 00:00:00'
    time_calendar = '365_day'

    attrs = {
        'var': {
            'long_name': 'Variable'
        }
    }

    ds = init_dataset(lon=lon_size, lat=lat_size, time=time,
                      time_units=time_units, time_calendar=time_calendar,
                      attrs=attrs, var=var)

    assert isinstance(ds, xr.Dataset)
    assert ds.sizes['lon'] == lon_size
    assert ds.sizes['lat'] == lat_size

    assert ds['time'].units == time_units
    assert ds['time'].calendar == time_calendar

    assert np.array_equal(ds['var'].values, var)
    assert ds['var'].long_name == attrs['var']['long_name']


def test_open_dataset():
    with open_dataset(dataset_path) as ds:
        assert isinstance(ds, xr.Dataset)
        assert ds['time'].dtype.type == np.datetime64


def test_open_dataset_no_cf():
    with open_dataset(dataset_path, decode_cf=False) as ds:
        assert isinstance(ds, xr.Dataset)
        assert ds['time'].dtype.type == np.float64


def test_load_dataset():
    with load_dataset(landseamask_path) as ds:
        assert isinstance(ds, xr.Dataset)


def test_write_dataset():
    test_path.unlink(missing_ok=True)

    ds = init_dataset()
    write_dataset(ds, test_path)


def test_order_variables():
    test_path.unlink(missing_ok=True)

    ds = init_dataset(
        var=np.random.rand(360, 720).astype(np.float64)
    )
    ds = ds[[*ds.data_vars, *ds.coords]]
    ds.to_netcdf(test_path)

    dataset = open_dataset_read(test_path)
    assert tuple(dataset.variables) == ('var', 'lon', 'lat')

    test_path.unlink(missing_ok=True)

    ds = order_variables(ds)
    ds.to_netcdf(test_path)

    dataset = open_dataset_read(test_path)
    assert tuple(dataset.variables) == ('lon', 'lat', 'var')


def test_get_attrs():
    with open_dataset(dataset_path) as ds:
        attrs = get_attrs(ds)
        assert attrs['lon']['long_name'] == 'Longitude'
        assert attrs['lat']['long_name'] == 'Latitude'
        assert attrs['tas']['long_name'] == 'Near-Surface Air Temperature'


def test_set_attrs():
    with open_dataset(dataset_path) as ds:
        attrs = get_attrs(ds)
        attrs['tas']['egg'] = 'spam'
        set_attrs(ds, attrs)
        assert attrs['tas']['egg'] == 'spam'


def test_add_fill_value_to_attrs():
    ds = xr.Dataset(
        coords={
            'time': np.arange(10, dtype=np.float64)
        },
        data_vars={
            'var': (['time'], np.ones(10))
        }
    )
    add_fill_value_to_attrs(ds)
    assert ds['time'].attrs['_FillValue'] == 1e20
    assert ds['var'].attrs['_FillValue'] == 1e20
    assert ds['var'].attrs['missing_value'] == 1e20


def test_set_fill_value_to_nan():
    ds = xr.Dataset(
        coords={
            'time': np.arange(10, dtype=np.float64)
        },
        data_vars={
            'var': (['time'], np.ones(10))
        }
    )
    ds['var'].values[0] = 1e20
    ds['var'].attrs['_FillValue'] = 1e20
    ds = set_fill_value_to_nan(ds)
    assert np.isnan(ds['var'].values[0])

def test_set_nan_to_fill_value():
    ds = xr.Dataset(
        coords={
            'time': np.arange(10, dtype=np.float64)
        },
        data_vars={
            'var': (['time'], np.ones(10))
        }
    )
    ds['var'].values[0] = np.nan
    ds['var'].attrs['_FillValue'] = 1e20
    ds = set_nan_to_fill_value(ds)
    assert ds['var'].values[0] == 1e20


def test_create_mask():
    ds = init_dataset(
        var=np.ones((360, 720))
    )

    geometry = box(-10, -5, 10, 5)

    df = gpd.GeoDataFrame(
        [{'geometry': geometry}],
        crs='EPSG:4326'  # WGS84 coordinate system
    )

    mask_ds = create_mask(ds, df, layer=0)

    assert mask_ds['lon'].shape == (720, )
    assert mask_ds['lat'].shape == (360, )

    assert mask_ds['mask'].dims == ('lat', 'lon')
    assert mask_ds['mask'].shape == (360, 720)

    inside_region = mask_ds.sel(lat=slice(5, -5), lon=slice(-10, 10))
    assert np.all(inside_region['mask'].values == 1.0)

    outside_regions = [
        mask_ds.sel(lon=slice(90, 5)),
        mask_ds.sel(lon=slice(-5, -90)),
        mask_ds.sel(lon=slice(10, 180)),
        mask_ds.sel(lon=slice(-180, -10))
    ]
    for outside_region in outside_regions:
        assert np.all(np.isnan(outside_region['mask'].values))


def test_to_dataframe():
    ds = xr.Dataset(
        coords={
            'time': np.arange(10, dtype=np.float64)
        },
        data_vars={
            'var': (['time'], np.ones(10))
        }
    )
    df = to_dataframe(ds)
    assert np.array_equal(df['time'], ds['time'])
    assert np.array_equal(df['var'], ds['var'])
