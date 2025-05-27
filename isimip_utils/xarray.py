import logging

import cftime
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


def open_dataset(path, decode_cf=False, load=False):
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
    logger.info(f'write {path.absolute()}')
    path.parent.mkdir(exist_ok=True, parents=True)

    for coord in ds.coords:
        ds.coords[coord].attrs["_FillValue"] = 1.e+20

    for var in ds.data_vars:
        ds.data_vars[var].attrs["_FillValue"] = 1.e+20

    # reorder the variables
    ds = ds[[*ds.coords, *ds.data_vars]]

    ds.to_netcdf(path, format='NETCDF4_CLASSIC')


def get_var_name(ds):
    return next(iter(ds.data_vars))


def get_var_units(ds):
    var_name = get_var_name(ds)
    return ds[var_name].units


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


def convert_to_dataframe(ds):
    ds.coords['time'] = ds.coords['time'].astype('datetime64[ns]')
    return ds.to_dataframe().reset_index()


def apply_fill_value(ds):
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
