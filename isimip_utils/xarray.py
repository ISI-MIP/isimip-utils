"""Functions for working with xarray datasets for ISIMIP data."""
import logging
from pathlib import Path

import cftime
import numpy as np
import pandas as pd
import xarray as xr

logger = logging.getLogger(__name__)


def init_dataset(lon: int = 720, lat: int = 360, time: np.array | None = None,
                 time_unit: str = 'days since 1601-1-1 00:00:00',
                 time_calendar: str = 'proleptic_gregorian',
                 attrs: dict = {}, **variables: list[np.array]) -> xr.Dataset:
    """Initialize a new xarray dataset with standard ISIMIP dimensions.

    Args:
        lon (int): Number of longitude points (default: 720).
        lat (int): Number of latitude points (default: 360).
        time (np.array | None): Time coordinate array, or None to omit time dimension (default: None).
        time_unit (str): Units for the time coordinate (default: 'days since 1601-1-1 00:00:00').
        time_calendar (str): Calendar type for time coordinate (default: 'proleptic_gregorian').
        attrs (dict): Dictionary of attributes for variables and global attributes.
        **variables (list[np.array]): Data variables to include in the dataset.

    Returns:
        Initialized xarray Dataset with coordinates and data variables.
    """

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


def open_dataset(path: str | Path, decode_cf: bool = False, load: bool = False) -> xr.Dataset:
    """Open a NetCDF dataset using xarray.

    Args:
        path (str | Path): Path to the NetCDF file.
        decode_cf (bool): Whether to decode CF conventions (default: False).
        load (bool): Whether to load data into memory immediately (default: False).

    Returns:
        Xarray Dataset object.

    Note:
        Handles non-standard time units like 'growing seasons' by converting
        them to 'common_years' with a 365_day calendar.
    """
    path = Path(path)

    logger.info(f'load {path.absolute()}' if load else f'open {path.absolute()}')

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


def write_dataset(ds: xr.Dataset, path: str | Path):
    """Write an xarray dataset to a NetCDF file.

    Args:
        ds (xr.Dataset): Xarray Dataset to write.
        path (str | Path): Path where the NetCDF file will be written.

    Note:
        Automatically adds fill values, converts NaN to fill values,
        orders variables, and sets time as unlimited dimension.
    """
    path = Path(path)
    path.parent.mkdir(exist_ok=True, parents=True)

    logger.info(f'write {path.absolute()}')

    ds = add_fill_value_to_attrs(ds)
    ds = set_nan_to_fill_value(ds)
    ds = order_variables(ds)

    # time should be an unlimited dimension
    unlimited_dims = ['time'] if 'time' in ds.dims else []

    ds.to_netcdf(path, format='NETCDF4_CLASSIC', unlimited_dims=unlimited_dims)


def order_variables(ds: xr.Dataset) -> xr.Dataset:
    """Reorder dataset variables with coordinates first, then data variables.

    Args:
        ds (xr.Dataset): Xarray Dataset to reorder.

    Returns:
        Dataset with reordered variables.
    """
    return ds[[*ds.coords, *ds.data_vars]]


def get_attrs(ds: xr.Dataset) -> dict:
    """Get all attributes from coordinates and data variables.

    Args:
        ds (xr.Dataset): Xarray Dataset.

    Returns:
        Dictionary mapping variable names to their attributes.
    """
    attrs = {}
    for coord in ds.coords:
        attrs[coord] = ds[coord].attrs
    for data_var in ds.data_vars:
        attrs[data_var] = ds[data_var].attrs
    return attrs


def set_attrs(ds: xr.Dataset, attrs: dict) -> xr.Dataset:
    """Set attributes on coordinates and data variables.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.
        attrs (dict): Dictionary mapping variable names to their attributes.

    Returns:
        Modified dataset with updated attributes.
    """
    for coord in ds.coords:
        if coord in attrs:
            ds[coord].attrs = attrs[coord]
    for data_var in ds.data_vars:
        if data_var in attrs:
            ds[data_var].attrs = attrs[data_var]
    return ds


def add_fill_value_to_attrs(ds: xr.Dataset) -> xr.Dataset:
    """Add _FillValue and missing_value attributes if not present.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.

    Returns:
        Dataset with fill value attributes added (default: 1.e+20).
    """
    for coord in ds.coords:
        if '_FillValue' not in ds.coords[coord].attrs:
            ds.coords[coord].attrs['_FillValue'] = 1.e+20

    for data_var in ds.data_vars:
        if '_FillValue' not in ds.data_vars[data_var].attrs:
            ds.data_vars[data_var].attrs['_FillValue'] = 1.e+20
        if 'missing_value' not in ds.data_vars[data_var].attrs:
            ds.data_vars[data_var].attrs['missing_value'] = 1.e+20
    return ds


def set_fill_value_to_nan(ds: xr.Dataset) -> xr.Dataset:
    """Replace fill values with NaN in data variables.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.

    Returns:
        Dataset with fill values replaced by NaN.
    """
    for var in ds.data_vars:
        fill_value = ds[var].attrs.get('_FillValue', 1e+20)
        ds[var] = ds[var].where(ds[var] != fill_value)
    return ds


def set_nan_to_fill_value(ds: xr.Dataset) -> xr.Dataset:
    """Replace NaN values with fill values in data variables.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.

    Returns:
        Dataset with NaN values replaced by fill values.
    """
    for var in ds.data_vars:
        fill_value = ds[var].attrs.get('_FillValue', 1e+20)
        ds[var] = ds[var].where(~np.isnan(ds[var]), fill_value)
    return ds


def create_mask(ds: xr.Dataset, df: pd.DataFrame, layer: int) -> xr.Dataset:
    """Create a spatial mask from a geometry layer.

    Args:
        ds (xr.Dataset): Xarray Dataset with lat/lon coordinates.
        df (pd.DataFrame): GeoDataFrame with geometry column.
        layer (int): Index of the layer to use from the GeoDataFrame.

    Returns:
        Xarray dataset with a 'mask' variable clipped to the geometry.

    Note:
        Requires geopandas and rioxarray to be installed.
    """
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


def to_dataframe(ds: xr.Dataset) -> pd.DataFrame:
    """Convert an xarray Dataset to a pandas DataFrame.

    Args:
        ds (xr.Dataset): Xarray Dataset to convert.

    Returns:
        Pandas DataFrame with coordinates as columns and data variables as columns.
            Attributes are preserved in df.attrs['coords'] and df.attrs['data_vars'].

    Note:
        Time coordinates are converted to datetime64[ns] format.
        Data variables are converted to float64.
    """
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
