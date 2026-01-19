"""Functions for working with xarray datasets for ISIMIP data."""
import logging
import warnings
from datetime import date, datetime
from pathlib import Path

import cftime
import numpy as np
import pandas as pd
import xarray as xr

logger = logging.getLogger(__name__)

DEFAULT_ATTRS = {
    'lon': {
        'standard_name': 'longitude',
        'long_name': 'Longitude',
        'units': 'degrees_east',
        'axis': 'X'
    },
    'lat': {
        'standard_name': 'latitude',
        'long_name': 'Latitude',
        'units': 'degrees_north',
        'axis': 'Y'
    },
    'time': {
        'standard_name': 'time',
        'long_name': 'Time',
        'calendar': 'proleptic_gregorian',
        'units': 'days since 1601-1-1 00:00:00',
        'axis': 'T'
    }
}

FILL_VALUE = 1e20

def init_dataset(lon: None | int | np.ndarray = 720,
                 lat: None | int | np.ndarray = 360,
                 time: None | int | np.ndarray = None,
                 dims: None | list = None,
                 attrs: None | dict = None,
                 **variables: np.ndarray) -> xr.Dataset:
    """Initialize a new xarray dataset with standard ISIMIP dimensions.

    Args:
        lon (int | np.ndarray): Number of longitude points, or longitude array, or None to omit (default: 720).
        lat (int | np.ndarray): Number of latitude points, or latitude array, or None to omit (default: 360).
        time (int | np.ndarray): Number of time steps, or time array, or None to omit time dimension (default: None).
        attrs (dict): Dictionary of attributes for variables and global attributes.
        dims (list): List of dimensions (default time, lat, lon).
        **variables (np.ndarray): Data variables to include in the dataset.

    Returns:
        Initialized xarray Dataset with coordinates and data variables.
    """

    # create dimensions
    if dims is None:
        dims = []
        if time is not None:
            dims.append('time')
        if lat is not None:
            dims.append('lat')
        if lon is not None:
            dims.append('lon')

    # create coordinates
    coords = {}
    if isinstance(lon, int):
        lon_delta = 360.0 / lon
        coords['lon'] = np.arange(-180 + 0.5 * lon_delta, 180, lon_delta)
    elif isinstance(lon, np.ndarray):
        coords['lon'] = lon

    if isinstance(lat, int):
        lat_delta = 180.0 / lat
        coords['lat'] = np.arange(90 - 0.5 * lat_delta, -90, -lat_delta)
    elif isinstance(lat, np.ndarray):
        coords['lat'] = lat

    if isinstance(time, int):
        coords['time'] = np.arange(time, dtype=np.float64)
    elif isinstance(time, np.ndarray):
        coords['time'] = time

    for dim in dims:
        if dim not in ['lon', 'lat', 'time']:
            coords[dim] = variables[dim]

    # create data variables
    data_vars = {
        var_name: (dims, var)
        for var_name, var in variables.items()
        if var_name not in dims
    }

    # create dataset
    ds = xr.Dataset(coords=coords, data_vars=data_vars)

    # combine attrs
    attrs = {
        key: {**DEFAULT_ATTRS.get(key, {}), **(attrs or {}).get(key, {})}
        for key in {*DEFAULT_ATTRS.keys(), *(attrs or {}).keys()}
    }

    # set attributes
    for coord in ds.coords:
        if coord in attrs:
            ds.coords[coord].attrs.update(attrs[coord])

    for data_var in ds.data_vars:
        if attrs:
            if data_var in attrs:
                ds.data_vars[data_var].attrs.update(attrs[data_var])

    # set global attributes
    ds.attrs = attrs.get('global', {})

    return ds


def open_dataset(path: str | Path, decode_cf: bool = True, load: bool = False) -> xr.Dataset:
    """Open a NetCDF dataset using xarray.

    Args:
        path (str | Path): Path to the NetCDF file.
        decode_cf (bool): Whether to decode CF conventions (default: True).
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

            ds['time'].attrs['long_name'] = 'Growing season'
            ds['time'].attrs['units'] = ''

            time_array = cftime.num2date(ds['time'].values, units=units, calendar='365_day')
            time = xr.DataArray(
                time_array,
                dims=['time'],
                coords={'time': time_array},
                name='time',
                attrs=ds['time'].attrs
            )

            ds = ds.assign_coords(time=time)

    if load:
        ds.load()

    return ds


def load_dataset(path: str | Path, decode_cf: bool = True) -> xr.Dataset:
    """Open a NetCDF dataset using xarray and load data into memory immediately.

    Args:
        path (str | Path): Path to the NetCDF file.
        decode_cf (bool): Whether to decode CF conventions (default: True).

    Returns:
        Xarray Dataset object.

    Note:
        Handles non-standard time units like 'growing seasons' by converting
        them to 'common_years' with a 365_day calendar.

        This is a shortcut for `open_dataset(path, decode_cf, load=True)`.
    """
    return open_dataset(path, decode_cf, load=True)


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

    ds = remove_fill_value_from_coords(ds)
    ds = add_fill_value_to_data_vars(ds)
    ds = set_nan_to_fill_value(ds)
    ds = order_variables(ds)

    # time should be an unlimited dimension
    unlimited_dims = ['time'] if 'time' in ds.dims else []

    # data variables should be compressed
    for data_var in ds.data_vars:
        ds[data_var].encoding.update({'zlib': True, 'complevel': 5})

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


def remove_fill_value_from_coords(ds: xr.Dataset) -> xr.Dataset:
    """Remove _FillValue and missing_value attributes from the coords.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.

    Returns:
        Dataset with fill value removed for the coords.
    """
    for coord in ds.coords:
        if '_FillValue' not in ds[coord].encoding:
            ds[coord].encoding['_FillValue'] = None
    return ds


def add_fill_value_to_data_vars(ds: xr.Dataset) -> xr.Dataset:
    """Add _FillValue and missing_value attributes to data_vars if not present.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.

    Returns:
        Dataset with fill value attributes added for the data_vars.
    """
    for data_var in ds.data_vars:
        if '_FillValue' not in ds.data_vars[data_var].attrs:
            ds.data_vars[data_var].attrs['_FillValue'] = FILL_VALUE
        if 'missing_value' not in ds.data_vars[data_var].attrs:
            missing_value = np.array(FILL_VALUE, dtype=ds[data_var].dtype)
            ds.data_vars[data_var].attrs['missing_value'] = missing_value
    return ds


def set_fill_value_to_nan(ds: xr.Dataset) -> xr.Dataset:
    """Replace fill values with NaN in data variables.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.

    Returns:
        Dataset with fill values replaced by NaN.
    """
    for data_var in ds.data_vars:
        fill_value = ds[data_var].attrs.get('_FillValue', FILL_VALUE)
        missing_value = np.array(fill_value, dtype=ds[data_var].dtype)
        ds[data_var] = ds[data_var].where(ds[data_var] != missing_value)
    return ds


def set_nan_to_fill_value(ds: xr.Dataset) -> xr.Dataset:
    """Replace NaN values with fill values in data variables.

    Args:
        ds (xr.Dataset): Xarray Dataset to modify.

    Returns:
        Dataset with NaN values replaced by fill values.
    """
    for data_var in ds.data_vars:
        fill_value = ds[data_var].attrs.get('_FillValue', FILL_VALUE)
        missing_value = np.array(fill_value, dtype=ds[data_var].dtype)
        ds[data_var] = ds[data_var].fillna(missing_value)
    return ds


def compute_time(ds: xr.Dataset, timestamp: datetime | None) -> float | None:
    """Convert a datetime to numeric time value for dataset.

    Args:
        ds (xr.Dataset): Dataset with time coordinate containing units and calendar.
        timestamp (datetime | date | None): Timestamp to convert, or None.

    Returns:
        Numeric time value in dataset's units, or None if timestamp is None.
    """
    if type(timestamp) is date:
        timestamp = datetime.combine(timestamp, datetime.min.time())

    units = ds.time.encoding.get('units') or ds.coords['time'].attrs.get('units')
    calendar = ds.time.encoding.get('calendar') or ds.coords['time'].attrs.get('calendar')
    return cftime.date2num(timestamp, units=units, calendar=calendar) if timestamp else None


def compute_offset(ds1: xr.Dataset, ds2: xr.Dataset) -> xr.DataArray | None:
    """Compute time offset between two datasets with different time units.

    Args:
        ds1 (xr.Dataset): First dataset with time coordinate.
        ds2 (xr.Dataset): Second dataset with time coordinate.

    Returns:
        Time offset to apply to ds2, or None if units/calendars match.
    """

    units1 = ds1.time.encoding.get('units') or ds1.coords['time'].attrs.get('units')
    calendar1 = ds1.time.encoding.get('calendar') or ds1.coords['time'].attrs.get('calendar')
    units2 = ds2.time.encoding.get('units') or ds2.coords['time'].attrs.get('units')
    calendar2 = ds2.time.encoding.get('calendar') or ds2.coords['time'].attrs.get('calendar')
    if units1 != units2 or calendar1 != calendar2:
        start_time = ds2['time'][0]
        start_date = cftime.num2date(start_time, units=units2, calendar=calendar2)
        offset = cftime.date2num(start_date, units=units1, calendar=calendar1) - start_time
        logger.debug(f'time axis diverges "{units1}"/"{units2}" "{calendar1}"/"{calendar2}" offset={offset.values}')
        return offset


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


def convert_time(time: np.ndarray, units='days since 1601-1-1 00:00:00', calendar='proleptic_gregorian') -> np.ndarray:
    """Convert an time coordinate array to np.float64 using cftime.date2num.

    Args:
        time (np.ndarray): Time coordinate array.
        units (str): Units for the time coordinate (default: 'days since 1601-1-1 00:00:00').
        calendar (str): Calendar type for time coordinate (default: 'proleptic_gregorian').

    Returns:
        time (np.ndarray): Time coordinate array as np.float64.
    """
    if np.issubdtype(time.dtype, np.floating) or np.issubdtype(time.dtype, np.integer):
        return time.astype(np.float64)

    if np.issubdtype(time.dtype, np.datetime64):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            if isinstance(time, pd.core.indexes.datetimes.DatetimeIndex):
                time = time.to_pydatetime()
            else:
                time = time.dt.to_pydatetime()

    if time.dtype == 'object' and isinstance(time[0], str):
        time = np.array([datetime.fromisoformat(t) for t in time], dtype=object)

    return cftime.date2num(
        time, calendar=calendar, units=units
    ).astype(np.float64)


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
        coord: ds[coord].attrs for coord in ds.coords if (ds[coord].size > 1)
    }
    df.attrs['data_vars'] = {
        data_var: ds[data_var].attrs for data_var in ds.data_vars if (ds[data_var].size > 1)
    }

    return df
