import logging
from pathlib import Path

import cftime
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


def init_dataset(lon=720, lat=360, time=None,
                 time_unit='days since 1601-1-1 00:00:00',
                 time_calendar='proleptic_gregorian', attrs={}, **variables):

    # create coordinates
    coords = {}
    if time is not None:
        coords['time'] = time

    lon_delta = 360.0 / lon
    lat_delta = 180.0 / lat

    coords['lon'] = np.arange(-180 + 0.5 * lon_delta, 180, lon_delta)
    coords['lat'] = np.arange(90 - 0.5 * lat_delta, -90, -lat_delta)

    # create data variables
    data_vars = {
        var_name: (['time', 'lon', 'lat'], var)
        for var_name, var in variables.items()
    }

    # create dataset
    ds = xr.Dataset(coords=coords, data_vars=data_vars)

    # set time attributes if time is set
    if time is not None:
        ds.coords['time'].attrs = {
            'standard_name': 'time',
            'long_name': 'Time',
            'units': time_unit,
            'calendar': time_calendar,
            'axis': 'T',
            '_FillValue': 1.e+20
        }

    # set lon attributes
    ds.coords['lon'].attrs = {
        'standard_name': 'longitude',
        'long_name': 'Longitude',
        'units': 'degrees_east',
        'axis': 'X',
        '_FillValue': 1.e+20
    }

    # set lon attributes
    ds.coords['lat'].attrs = {
        'standard_name': 'latitude',
        'long_name': 'Latitude',
        'units': 'degrees_north',
        'axis': 'Y',
        '_FillValue': 1.e+20
    }

    # set variable attributes
    for data_var in ds.data_vars:
        if data_var in attrs:
            ds.data_vars[data_var].attrs.update(attrs[data_var])

        ds.data_vars[data_var].attrs["_FillValue"] = 1.e+20

    # set global attributes
    ds.attrs = attrs.get('global', {})

    return ds


def open_dataset(path, decode_cf=False, load=False):
    path = Path(path)

    if not load:
        logger.info(f'open {path.absolute()}')
    else:
        logger.info(f'load {path.absolute()}')

    try:
        ds = xr.open_dataset(path, decode_cf=decode_cf)
    except ValueError:
        # workaround for non standard times (e.g. growing seasons)
        ds = xr.open_dataset(path, decode_cf=decode_cf, decode_times=False)

        if ds['time'].units.startswith('growing seasons'):
            units = ds['time'].units.replace('growing seasons', 'common_years')
            times = cftime.num2date(ds['time'], units, calendar='365_day')
            ds['time'] = times

    if load:
        ds.load()

    return ds


def load_dataset(path, decode_cf=False):
    return open_dataset(path, decode_cf=False, load=True)


def write_dataset(ds, path):
    path = Path(path)
    path.parent.mkdir(exist_ok=True, parents=True)

    logger.info(f'write {path.absolute()}')

    ds = add_fill_value_to_attrs(ds)
    ds = order_variables(ds)

    # time should be an unlimited dimension
    unlimited_dims = ['time'] if 'time' in ds.dims else []

    ds.to_netcdf(path, format='NETCDF4_CLASSIC', unlimited_dims=unlimited_dims)


def order_variables(ds):
    return ds[[*ds.coords, *ds.data_vars]]


def get_attrs(ds):
    attrs = {}
    for coord in ds.coords:
        attrs[coord] = ds[coord].attrs
    for data_var in ds.data_vars:
        attrs[data_var] = ds[data_var].attrs
    return attrs


def set_attrs(ds, attrs):
    for coord in ds.coords:
        if coord in attrs:
            ds[coord].attrs = attrs[coord]
    for data_var in ds.data_vars:
        if data_var in attrs:
            ds[data_var].attrs = attrs[data_var]
    return ds


def add_fill_value_to_attrs(ds):
    for coord in ds.coords:
        if '_FillValue' not in ds.coords[coord].attrs:
            ds.coords[coord].attrs['_FillValue'] = 1.e+20

    for data_var in ds.data_vars:
        if '_FillValue' not in ds.data_vars[data_var].attrs:
            ds.data_vars[data_var].attrs['_FillValue'] = 1.e+20
        if 'missing_value' not in ds.data_vars[data_var].attrs:
            ds.data_vars[data_var].attrs['missing_value'] = 1.e+20
    return ds


def to_dataframe(ds):
    if 'time' in ds.coords:
        ds.coords['time'] = ds.coords['time'].astype('datetime64[ns]')

    ds = ds.assign({
        data_var: ds[data_var].astype('float64')
        for data_var in ds.data_vars
    })

    df = ds.to_dataframe().reset_index()
    df.attrs['coords'] = {
        coord: ds[coord].attrs for coord in ds.coords
    }
    df.attrs['data_vars'] = {
        data_var: ds[data_var].attrs for data_var in ds.data_vars
    }

    return df


def set_fill_value_to_nan(ds):
    for var in ds.data_vars:
        fill_value = ds[var].attrs.get('_FillValue', 1e+20)
        ds[var] = ds[var].where(ds[var] != fill_value)
    return ds


def create_mask(ds, df, layer):
    import shapely.geometry
    logger.info('create mask')

    df_row = df.iloc[layer]
    geometry = shapely.geometry.mapping(df_row['geometry'])

    ds_lat = ds.coords['lat']
    ds_lon = ds.coords['lon']
    mask_ds = xr.Dataset(
        data_vars={
            'mask': (('lat', 'lon'), np.ones((ds_lat.size, ds_lon.size), dtype=np.float32))
        },
        coords={'lat': ds_lat, 'lon': ds_lon}
    )
    mask_ds.rio.write_crs(df.crs, inplace=True)
    mask_ds = mask_ds.rio.clip([geometry], drop=False)
    mask_ds = mask_ds.drop_vars('spatial_ref')
    return mask_ds
