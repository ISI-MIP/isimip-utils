"""Data extraction and manipulation utilities for xarray datasets."""
import logging
from datetime import datetime

import numpy as np
import xarray as xr

from isimip_utils.exceptions import ExtractionError
from isimip_utils.utils import validate_lat, validate_lon
from isimip_utils.xarray import compute_offset, compute_time

logger = logging.getLogger(__name__)


def select_time(ds: xr.Dataset, timestamp: datetime) -> xr.Dataset | None:
    """Select a single time point from a dataset.

    Args:
        ds (xr.Dataset): Dataset with time dimension.
        timestamp (datetime): Timestamp to select.

    Returns:
        Dataset at the selected time, or None if timestamp is outside range.
    """
    logger.info(f'select time time={timestamp}')
    if ds.time.encoding.get('units'):
        time = np.datetime64(timestamp)
    else:
        time = compute_time(ds, timestamp)

    if time < ds['time'].min() or time > ds['time'].max():
        logger.warn(f'Selected time={time} is outside the dataset.')
        return None

    return ds.sel(time=time, method='nearest')


def select_period(ds: xr.Dataset, start: datetime | None, end: datetime | None) -> xr.Dataset:
    """Select a time period from a dataset.

    Args:
        ds (xr.Dataset): Dataset with time dimension.
        start (datetime | None): Start of period, or None for beginning.
        end (datetime | None): End of period, or None for end.

    Returns:
        Dataset with time dimension sliced to the period.

    Raises:
        ExtractionError: If no time axis remains after selection.
    """
    logger.info(f'select period start={start} end={end}')
    if ds.time.encoding.get('units'):
        start_time, end_time = np.datetime64(start), np.datetime64(end)
    else:
        start_time, end_time = compute_time(ds, start), compute_time(ds, end)

    ds = ds.sel(time=slice(start_time, end_time))

    if 'time' not in ds.sizes:
        raise ExtractionError('No time axis remains after selecting period.')

    return ds


def select_point(ds: xr.Dataset, lat: float, lon: float) -> xr.Dataset:
    """Select a single geographic point from a dataset.

    Args:
        ds (xr.Dataset): Dataset with lat/lon dimensions.
        lat (float): Latitude (-90 to 90).
        lon (float): Longitude (-180 to 180).

    Returns:
        Dataset at the nearest grid point.

    Raises:
        ValidationError: If lat/lon are out of valid range.
    """
    logger.info(f'select point lat={lat} lon={lon}')
    validate_lat(lat)
    validate_lon(lon)
    return ds.sel(lat=lat, lon=lon, method='nearest')


def select_bbox(ds: xr.Dataset, west: float, east: float, south: float, north: float) -> xr.Dataset:
    """Select a bounding box region from a dataset.

    Args:
        ds (xr.Dataset): Dataset with lat/lon dimensions.
        west (float): Western longitude boundary (-180 to 180).
        east (float): Eastern longitude boundary (-180 to 180).
        south (float): Southern latitude boundary (-90 to 90).
        north (float): Northern latitude boundary (-90 to 90).

    Returns:
        Dataset with lat/lon dimensions sliced to the bounding box.

    Raises:
        ValidationError: If coordinates are out of valid range.
        ExtractionError: If no lat or lon axis remains after selection.
    """
    logger.info(f'cutout bbox west={west} east={east} south={south} east={north}')

    validate_lat(south)
    validate_lat(north)
    validate_lon(west)
    validate_lon(east)

    lat_slice = slice(north, south) if ds.lon.values[1] > ds.lon.values[0] else slice(south, north)
    lon_slice = slice(west, east)

    ds = ds.sel(lat=lat_slice, lon=lon_slice)

    if 'lat' not in ds.sizes:
        raise ExtractionError('No lat axis remains after selecting bbox.')
    elif 'lon' not in ds.sizes:
        raise ExtractionError('No lon axis remains after selecting bbox.')

    return ds


def mask_bbox(ds: xr.Dataset, west: float, east: float, south: float, north: float) -> xr.Dataset:
    """Mask a dataset to a bounding box, setting values outside to NaN.

    Args:
        ds (xr.Dataset): Dataset with lat/lon dimensions.
        west (float): Western longitude boundary (-180 to 180).
        east (float): Eastern longitude boundary (-180 to 180).
        south (float): Southern latitude boundary (-90 to 90).
        north (float): Northern latitude boundary (-90 to 90).

    Returns:
        Dataset with values outside bounding box masked as NaN.

    Raises:
        ValidationError: If coordinates are out of valid range.
    """
    logger.info(f'cutout bbox west={west} east={east} south={south} east={north}')

    validate_lat(south)
    validate_lat(north)
    validate_lon(west)
    validate_lon(east)

    lat = ds['lat']
    lon = ds['lon']

    if west > east:
        lon_mask = (lon >= west) | (lon <= east)
    else:
        lon_mask = (lon >= west) & (lon <= east)

    lat_mask = (lat >= south) & (lat <= north)

    mask = lat_mask & lon_mask

    ds = ds.where(mask)

    return ds


def mask_mask(ds: xr.Dataset, mask_ds: xr.Dataset, mask_var: str = 'mask',
              inverse: bool = False) -> xr.Dataset:
    """Apply a mask dataset to another dataset.

    Args:
        ds (xr.Dataset): Dataset to mask.
        mask_ds (xr.Dataset): Dataset containing mask variable.
        mask_var (str): Name of mask variable (default: 'mask').
        inverse (bool): Whether to invert the mask (default: False).

    Returns:
        Masked dataset with values where mask is 1 (or 0 if inverse=True).
    """
    logger.info(f'mask {mask_var}')
    return ds.where(np.isclose(mask_ds[mask_var], 0 if inverse else 1))


def compute_spatial_average(ds: xr.Dataset, weights: xr.DataArray | None = None) -> xr.Dataset:
    """Compute spatial average over lat/lon dimensions.

    Args:
        ds (xr.Dataset): Dataset with lat/lon dimensions.
        weights (xr.DataArray | None): Weights for averaging. If None, uses latitude-dependent weights.

    Returns:
        Dataset with lat/lon dimensions averaged out.
    """
    logger.info('compute spatial average')

    if weights is None:
        logger.warn('no weights provided, using latitude-dependent weights')
        weights = np.sin(np.deg2rad(ds.lat + 0.25)) - np.sin(np.deg2rad(ds.lat - 0.25))

    return ds.weighted(weights).mean(dim=('lat', 'lon'), skipna=True).astype(np.float32)


def compute_temporal_average(ds: xr.Dataset) -> xr.Dataset:
    """Compute temporal average over time dimension.

    Args:
        ds (xr.Dataset): Dataset with time dimension.

    Returns:
        Dataset with time dimension averaged out.
    """
    logger.info('compute temporal average')
    return ds.mean(dim='time', skipna=True).astype(np.float32)


def count_values(ds: xr.Dataset) -> xr.Dataset:
    """Count non-NaN values over lat/lon dimensions.

    Args:
        ds (xr.Dataset): Dataset with lat/lon dimensions.

    Returns:
        Dataset with count of non-NaN values per time step.
    """
    logger.info('count values')
    return ds.count(dim=('lat', 'lon')).astype(np.float32)


def concat_extraction(ds1: xr.Dataset | None, ds2: xr.Dataset) -> xr.Dataset:
    """Concatenate two datasets along time dimension with offset correction.

    Args:
        ds1 (xr.Dataset | None): First dataset, or None.
        ds2 (xr.Dataset): Second dataset to concatenate.

    Returns:
        Concatenated dataset, or copy of ds2 if ds1 is None.
    """
    if ds1 is None:
        return ds2.copy()
    elif not ds2.sizes.get('time'):
        return ds1
    else:
        if not ds1.time.encoding:
            # apply offset when time units or calendar diverges, but only if times where not decoded
            offset = compute_offset(ds1, ds2)
            if offset is not None:
                ds2 = ds2.assign_coords(time=ds2['time'] + offset)

        return xr.concat([ds1, ds2], 'time')
