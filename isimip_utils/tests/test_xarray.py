from datetime import timedelta

import cftime
import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

from isimip_utils.netcdf import open_dataset_read
from isimip_utils.tests import constants, helper
from isimip_utils.xarray import (
    add_compression_to_data_vars,
    add_fill_value_to_data_vars,
    convert_time,
    create_mask,
    get_attrs,
    init_dataset,
    load_dataset,
    open_dataset,
    order_variables,
    remove_fill_value_from_coords,
    set_attrs,
    to_dataframe,
    write_dataset,
)


def test_init_dataset():
    ds = init_dataset()

    assert isinstance(ds, xr.Dataset)
    assert ds.sizes['lon'] == 720
    assert ds.sizes['lat'] == 360

    test_path = constants.OUTPUT_PATH / 'test.nc'
    test_path.unlink(missing_ok=True)

    write_dataset(ds, test_path)

    output = helper.call(f'ncdump -h {test_path}')

    helper.assert_multiline_strings_equal(output, '''
netcdf test {
dimensions:
    lon = 720 ;
    lat = 360 ;
variables:
    double lon(lon) ;
        lon:standard_name = "longitude" ;
        lon:long_name = "Longitude" ;
        lon:units = "degrees_east" ;
        lon:axis = "X" ;
    double lat(lat) ;
        lat:standard_name = "latitude" ;
        lat:long_name = "Latitude" ;
        lat:units = "degrees_north" ;
        lat:axis = "Y" ;
}
''')


def test_init_dataset_float():
    lon_size, lat_size = 18, 9

    var = np.random.rand(lat_size, lon_size).astype(np.float32)

    attrs = {
        'var': {
            'long_name': 'Variable'
        }
    }

    ds = init_dataset(lon=lon_size, lat=lat_size, var=var, attrs=attrs)

    assert isinstance(ds, xr.Dataset)
    assert ds.sizes['lon'] == lon_size
    assert ds.sizes['lat'] == lat_size

    test_path = constants.OUTPUT_PATH / 'test.nc'
    test_path.unlink(missing_ok=True)

    write_dataset(ds, test_path)

    output = helper.call(f'ncdump -h {test_path}')

    helper.assert_multiline_strings_equal(output, '''
netcdf test {
dimensions:
    lon = 18 ;
    lat = 9 ;
variables:
    double lon(lon) ;
        lon:standard_name = "longitude" ;
        lon:long_name = "Longitude" ;
        lon:units = "degrees_east" ;
        lon:axis = "X" ;
    double lat(lat) ;
        lat:standard_name = "latitude" ;
        lat:long_name = "Latitude" ;
        lat:units = "degrees_north" ;
        lat:axis = "Y" ;
    float var(lat, lon) ;
        var:_FillValue = 1.e+20f ;
        var:long_name = "Variable" ;
        var:missing_value = 1.e+20f ;
}
''')

def test_init_dataset_double():
    lon_size, lat_size = 18, 9

    var = np.random.rand(lat_size, lon_size).astype(np.float64)

    attrs = {
        'var': {
            'long_name': 'Variable'
        }
    }

    ds = init_dataset(lon=lon_size, lat=lat_size, var=var, attrs=attrs)

    assert isinstance(ds, xr.Dataset)
    assert ds.sizes['lon'] == lon_size
    assert ds.sizes['lat'] == lat_size

    test_path = constants.OUTPUT_PATH / 'test.nc'
    test_path.unlink(missing_ok=True)

    write_dataset(ds, test_path)

    output = helper.call(f'ncdump -h {test_path}')

    helper.assert_multiline_strings_equal(output, '''
netcdf test {
dimensions:
    lon = 18 ;
    lat = 9 ;
variables:
    double lon(lon) ;
        lon:standard_name = "longitude" ;
        lon:long_name = "Longitude" ;
        lon:units = "degrees_east" ;
        lon:axis = "X" ;
    double lat(lat) ;
        lat:standard_name = "latitude" ;
        lat:long_name = "Latitude" ;
        lat:units = "degrees_north" ;
        lat:axis = "Y" ;
    double var(lat, lon) ;
        var:_FillValue = 1.e+20 ;
        var:long_name = "Variable" ;
        var:missing_value = 1.e+20 ;
}
''')

def test_init_dataset_args():
    lon_size, lat_size, time_size = 180, 90, 10

    time = np.arange(time_size, dtype=np.float64)
    var = np.random.rand(time_size, lat_size, lon_size).astype(np.float32)

    attrs = {
        'var': {
            'long_name': 'Variable'
        },
        'time': {
            'calendar': '365_day',
            'units': 'days since 2000-01-01 00:00:00'
        }
    }

    ds = init_dataset(lon=lon_size, lat=lat_size, time=time, attrs=attrs, var=var)

    assert isinstance(ds, xr.Dataset)
    assert ds.sizes['lon'] == lon_size
    assert ds.sizes['lat'] == lat_size

    assert ds['time'].units == attrs['time']['units']
    assert ds['time'].calendar == attrs['time']['calendar']

    assert np.array_equal(ds['var'].values, var)
    assert ds['var'].long_name == attrs['var']['long_name']

    test_path = constants.OUTPUT_PATH / 'test.nc'
    test_path.unlink(missing_ok=True)

    write_dataset(ds, test_path)

    output = helper.call(f'ncdump -h {test_path}')

    helper.assert_multiline_strings_equal(output, '''
netcdf test {
dimensions:
    time = UNLIMITED ; // (10 currently)
    lon = 180 ;
    lat = 90 ;
variables:
    double lon(lon) ;
        lon:standard_name = "longitude" ;
        lon:long_name = "Longitude" ;
        lon:units = "degrees_east" ;
        lon:axis = "X" ;
    double lat(lat) ;
        lat:standard_name = "latitude" ;
        lat:long_name = "Latitude" ;
        lat:units = "degrees_north" ;
        lat:axis = "Y" ;
    double time(time) ;
        time:standard_name = "time" ;
        time:long_name = "Time" ;
        time:calendar = "365_day" ;
        time:units = "days since 2000-01-01 00:00:00" ;
        time:axis = "T" ;
    float var(time, lat, lon) ;
        var:_FillValue = 1.e+20f ;
        var:long_name = "Variable" ;
        var:missing_value = 1.e+20f ;
}
''')


def test_init_dataset_latlon():
    var = np.random.rand(10, 1, 1).astype(np.float32)

    attrs = {
        'var': {
            'long_name': 'Variable'
        }
    }

    ds = init_dataset(
        lon=np.array([10], dtype=np.float64),
        lat=np.array([20], dtype=np.float64),
        time=10, attrs=attrs, var=var
    )

    assert isinstance(ds, xr.Dataset)
    assert ds.sizes['lon'] == 1
    assert ds.sizes['lat'] == 1

    assert ds['time'].units == 'days since 1601-1-1 00:00:00'
    assert ds['time'].calendar == 'proleptic_gregorian'

    assert np.array_equal(ds['var'].values, var)
    assert ds['var'].long_name == attrs['var']['long_name']

    test_path = constants.OUTPUT_PATH / 'test.nc'
    test_path.unlink(missing_ok=True)

    write_dataset(ds, test_path)

    output = helper.call(f'ncdump -h {test_path}')

    helper.assert_multiline_strings_equal(output, '''
netcdf test {
dimensions:
    time = UNLIMITED ; // (10 currently)
    lon = 1 ;
    lat = 1 ;
variables:
    double lon(lon) ;
        lon:standard_name = "longitude" ;
        lon:long_name = "Longitude" ;
        lon:units = "degrees_east" ;
        lon:axis = "X" ;
    double lat(lat) ;
        lat:standard_name = "latitude" ;
        lat:long_name = "Latitude" ;
        lat:units = "degrees_north" ;
        lat:axis = "Y" ;
    double time(time) ;
        time:standard_name = "time" ;
        time:long_name = "Time" ;
        time:calendar = "proleptic_gregorian" ;
        time:units = "days since 1601-1-1 00:00:00" ;
        time:axis = "T" ;
    float var(time, lat, lon) ;
        var:_FillValue = 1.e+20f ;
        var:long_name = "Variable" ;
        var:missing_value = 1.e+20f ;
}
''')


def test_init_dataset_dims():
    a = np.arange(0, 2, dtype=np.float64)
    b = np.arange(0, 3, dtype=np.float64)
    var = np.random.rand(b.size, a.size, 360, 720).astype(np.float32)

    attrs = {
        'var': {
            'long_name': 'Variable'
        },
        'a': {
            'long_name': 'A Axis',
            'axis': 'A'
        },
        'b': {
            'long_name': 'B Axis',
            'axis': 'B'
        }
    }

    ds = init_dataset(dims=('b', 'a', 'lat', 'lon'), attrs=attrs, a=a, b=b, var=var)

    assert isinstance(ds, xr.Dataset)

    assert ds['a'].long_name == attrs['a']['long_name']
    assert ds['b'].long_name == attrs['b']['long_name']

    assert np.array_equal(ds['var'].values, var)
    assert ds['var'].long_name == attrs['var']['long_name']

    test_path = constants.OUTPUT_PATH / 'test.nc'
    test_path.unlink(missing_ok=True)

    write_dataset(ds, test_path)

    output = helper.call(f'ncdump -h {test_path}')

    helper.assert_multiline_strings_equal(output, '''
netcdf test {
dimensions:
    lon = 720 ;
    lat = 360 ;
    b = 3 ;
    a = 2 ;
variables:
    double lon(lon) ;
        lon:standard_name = "longitude" ;
        lon:long_name = "Longitude" ;
        lon:units = "degrees_east" ;
        lon:axis = "X" ;
    double lat(lat) ;
        lat:standard_name = "latitude" ;
        lat:long_name = "Latitude" ;
        lat:units = "degrees_north" ;
        lat:axis = "Y" ;
    double b(b) ;
        b:long_name = "B Axis" ;
        b:axis = "B" ;
    double a(a) ;
        a:long_name = "A Axis" ;
        a:axis = "A" ;
    float var(b, a, lat, lon) ;
        var:_FillValue = 1.e+20f ;
        var:long_name = "Variable" ;
        var:missing_value = 1.e+20f ;
}
''')


def test_open_dataset():
    with open_dataset(constants.DATASETS_PATH / constants.TAS_PATH) as ds:
        assert isinstance(ds, xr.Dataset)
        assert ds['time'].dtype.type == np.datetime64


def test_open_dataset_decode_cf_false():
    with open_dataset(constants.DATASETS_PATH / constants.TAS_PATH, decode_cf=False) as ds:
        assert isinstance(ds, xr.Dataset)
        assert ds['time'].dtype.type == np.float64


def test_open_dataset_growing_seasons():
    with open_dataset(constants.DATASETS_PATH / constants.YIELD_PATH) as ds:
        assert isinstance(ds, xr.Dataset)
        assert isinstance(ds['time'].dtype, object)
        assert ds['time'].values[0].isoformat() == '1901-01-01T00:00:00'


def test_load_dataset():
    with load_dataset(constants.DATASETS_PATH / constants.LANDSEAMASK_PATH) as ds:
        assert isinstance(ds, xr.Dataset)


def test_order_variables():
    test_path = constants.OUTPUT_PATH / 'test.nc'
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
    with open_dataset(constants.DATASETS_PATH / constants.TAS_PATH) as ds:
        attrs = get_attrs(ds)
        assert attrs['lon']['long_name'] == 'Longitude'
        assert attrs['lat']['long_name'] == 'Latitude'
        assert attrs['tas']['long_name'] == 'Near-Surface Air Temperature'


def test_set_attrs():
    with open_dataset(constants.DATASETS_PATH / constants.TAS_PATH) as ds:
        attrs = get_attrs(ds)
        attrs['tas']['egg'] = 'spam'
        set_attrs(ds, attrs)
        assert attrs['tas']['egg'] == 'spam'


def test_remove_fill_value_from_coords():
    ds = xr.Dataset(
        coords={
            'time': np.arange(10, dtype=np.float64)
        },
        data_vars={
            'var': (['time'], np.ones(10))
        }
    )
    remove_fill_value_from_coords(ds)
    assert '_FillValue' not in ds['time']


def test_add_fill_value_to_data_vars():
    ds = xr.Dataset(
        coords={
            'time': np.arange(10, dtype=np.float64)
        },
        data_vars={
            'var': (['time'], np.ones(10))
        }
    )

    assert not ds['var'].encoding

    add_fill_value_to_data_vars(ds)

    assert ds['var'].encoding.get('_FillValue') == 1e20
    assert ds['var'].encoding.get('missing_value') == 1e20


def test_add_compression_to_data_vars():
    ds = xr.Dataset(
        coords={
            'time': np.arange(10, dtype=np.float64)
        },
        data_vars={
            'var': (['time'], np.ones(10))
        }
    )

    assert not ds['var'].encoding

    add_compression_to_data_vars(ds, 9)

    assert ds['var'].encoding.get('zlib') is True
    assert ds['var'].encoding.get('complevel') == 9


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


def test_convert_time_datetime():
    calendar = 'proleptic_gregorian'
    units = 'days since 2000-01-01 00:00:00'

    start_day = cftime.datetime(2000, 1, 1, calendar=calendar)
    end_day = cftime.datetime(2000, 12, 31, calendar=calendar)

    time = np.array([start_day + timedelta(days=i) for i in range((end_day - start_day).days + 1)], dtype=object)
    time_converted = convert_time(time, calendar=calendar, units=units)

    start = 0
    assert np.array_equal(time_converted, np.arange(start, start + 366, dtype=np.float64))


def test_convert_time_datetime64():
    time = np.array(pd.date_range(start='2000-01-01', end='2000-12-31', freq='D'))
    time_converted = convert_time(time)

    start = 145731
    assert np.array_equal(time_converted, np.arange(start, start + 366, dtype=np.float64))


def test_convert_time_datetime64_index():
    time = pd.date_range(start='2000-01-01', end='2000-12-31', freq='D')
    time_converted = convert_time(time)

    start = 145731
    assert np.array_equal(time_converted, np.arange(start, start + 366, dtype=np.float64))


def test_convert_time_datetime64_series():
    time = pd.Series(pd.date_range(start='2000-01-01', end='2000-12-31', freq='D'))
    time_converted = convert_time(time)

    start = 145731
    assert np.array_equal(time_converted, np.arange(start, start + 366, dtype=np.float64))


def test_convert_time_datetime_str():
    time = pd.date_range(start='2000-01-01', end='2000-12-31', freq='D').astype(str)
    time_converted = convert_time(time)

    start = 145731
    assert np.array_equal(time_converted, np.arange(start, start + 366, dtype=np.float64))


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
