import logging

import cftime
import numpy as np
import xarray as xr

from isimip_utils.exceptions import ExtractionError, ValidationError

logger = logging.getLogger(__name__)


def select_time(ds, timestamp):
    logger.info(f'select time time={timestamp}')
    time = compute_time(ds, timestamp)
    if time < 0 or time > ds['time'].max():
        logger.warn(f'Selected time={time} is outside the dataset.')
        return None
    else:
        return ds.sel(time=time, method='nearest')


def select_period(ds, start, end):
    logger.info(f'select period start={start} end={end}')
    units = ds.coords['time'].attrs['units']
    calendar = ds.coords['time'].attrs['calendar']

    start_time = cftime.date2num(start, units=units, calendar=calendar) if start else None
    end_time = cftime.date2num(end, units=units, calendar=calendar) if end else None

    ds = ds.sel(time=slice(start_time, end_time))

    if 'time' not in ds.sizes:
        raise ExtractionError('No time axis remains after selecting period.')

    return ds


def select_point(ds, lat, lon):
    logger.info(f'select point lat={lat} lon={lon}')
    validate_lat(lat)
    validate_lon(lon)
    return ds.sel(lat=lat, lon=lon, method='nearest')


def select_bbox(ds, west, east, south, north):
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


def mask_bbox(ds, west, east, south, north):
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


def mask_mask(ds, mask_ds, mask_var='mask'):
    logger.info(f'mask {mask_var}')
    return ds.where(mask_ds[mask_var] == 1)


def compute_spatial_average(ds, weights=None):
    logger.info('compute spatial average')

    if weights is None:
        logger.warn('no weights provided, using latitude-dependent weights')
        weights = np.sin(np.deg2rad(ds.lat + 0.25)) - np.sin(np.deg2rad(ds.lat - 0.25))

    return ds.weighted(weights).mean(dim=('lat', 'lon'), skipna=True).astype(np.float32)


def compute_temporal_average(ds):
    logger.info('compute temporal average')
    return ds.mean(dim='time', skipna=True).astype(np.float32)


def count_values(ds):
    logger.info('count values')
    return ds.count(dim=('lat', 'lon')).astype(np.float32)


def concat_extraction(ds1, ds2):
    if ds1 is None:
        return ds2.copy()
    elif 'time' not in ds2.sizes:
        return ds1
    else:
        # apply offset when time units or calendar diverges
        offset = compute_offset(ds1, ds2)
        if offset is not None:
            ds2 = ds2.assign_coords(time=ds2['time'] + offset)

        return xr.concat([ds1, ds2], 'time')


def compute_time(ds, timestamp):
    units = ds.coords['time'].attrs['units']
    calendar = ds.coords['time'].attrs['calendar']
    return cftime.date2num(timestamp, units=units, calendar=calendar) if timestamp else None


def compute_offset(ds1, ds2):
    units1 = ds1.coords['time'].attrs['units']
    units2 = ds2.coords['time'].attrs['units']
    calendar1 = ds1.coords['time'].attrs['calendar']
    calendar2 = ds2.coords['time'].attrs['calendar']

    if units1 != units2 or calendar1 != calendar2:
        start_time = ds2['time'][0]
        start_date = cftime.num2date(start_time, units=units2, calendar=calendar2)
        offset = cftime.date2num(start_date, units=units1, calendar=calendar1) - start_time
        logger.debug(f'time axis diverges "{units1}"/"{units2}" "{calendar1}"/"{calendar2}" offset={offset.values}')
        return offset


def validate_lat(lat):
    if lat < -90:
        raise ValidationError(f'lat={lat} must be > -90')
    elif lat > 90:
        raise ValidationError(f'lat={lat} must be < 90')


def validate_lon(lon):
    if lon < -180:
        raise ValidationError(f'lon={lon} must be > -180')
    elif lon > 180:
        raise ValidationError(f'lon={lon} must be < 180')
