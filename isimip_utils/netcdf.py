"""Functions to open and read NetCDF files using netCDF4."""
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from netCDF4 import Dataset

FILL_VALUE = 1e+20
LIST_TYPES = [np.ndarray]
FLOAT_TYPES = [np.float32, np.float64]
INT_TYPES = [np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32, np.int64, np.uint64]


def open_dataset_read(file_path: str | Path) -> Dataset:
    """Open a NetCDF dataset in read-only mode.

    Args:
        file_path (str | Path): Path to the NetCDF file.

    Returns:
        NetCDF4 Dataset object opened in read mode.
    """
    return Dataset(file_path, 'r')


def open_dataset_write(file_path: str | Path) -> Dataset:
    """Open a NetCDF dataset in read/write mode.

    Args:
        file_path (str | Path): Path to the NetCDF file.

    Returns:
        NetCDF4 Dataset object opened in read/write mode.
    """
    return Dataset(file_path, 'r+')


def init_dataset(file_path: str | Path, diskless: bool = False, overwrite: bool = False, lon: int = 720, lat: int = 360,
                 time: None | np.ndarray = None, time_unit: str = 'days since 1601-1-1 00:00:00',
                 time_calendar: str = 'proleptic_gregorian', attrs: dict = {}, **variables: Any) -> Dataset:
    """Initialize a new NetCDF4 dataset with standard dimensions and variables.

    Args:
        file_path (str | Path): Path where the NetCDF file will be created.
        diskless (bool): If True, create dataset in memory (default: False).
        overwrite (bool): If True, overwrite existing dataset (default: False).
        lon (int): Number of longitude points (default: 720).
        lat (int): Number of latitude points (default: 360).
        time (None | np.ndarray): Time dimension configuration (default: None).
        time_unit (str): Units for the time dimension (default: 'days since 1601-1-1 00:00:00').
        time_calendar (str): Calendar type for time dimension (default: 'proleptic_gregorian').
        attrs (dict): Dictionary of attributes for variables and global attributes.
        **variables (Any): Data variables to create in the dataset.

    Returns:
        Initialized NetCDF4 Dataset object.
    """
    # overwrite existing file
    if overwrite and file_path.exists():
        file_path.unlink()

    # create NetCDF dataset
    ds = Dataset(file_path, 'w', format='NETCDF4_CLASSIC', diskless=diskless)

    # create time dimension if time is set
    if time is not None and time is not False:
        ds.createDimension('time', None)

    # create lon and lat dimensions
    ds.createDimension('lon', lon)
    ds.createDimension('lat', lat)

    # create time variable if time is set
    if time is not None:
        time_variable = ds.createVariable('time', 'f8', ('time',), fill_value=FILL_VALUE)
        time_variable.missing_value = FILL_VALUE
        time_variable.standard_name = 'time'
        time_variable.long_name = 'Time'
        time_variable.units = time_unit
        time_variable.calendar = time_calendar

        if isinstance(time, np.ndarray):
            time_variable[:] = time

    # create lon variable
    lon_delta = 360.0 / lon
    lon_variable = ds.createVariable('lon', 'f8', ('lon',), fill_value=FILL_VALUE)
    lon_variable.missing_value = FILL_VALUE
    lon_variable.standard_name = 'longitude'
    lon_variable.long_name = 'Longitude'
    lon_variable.units = 'degrees_east'
    lon_variable.axis = 'X'
    lon_variable[:] = np.arange(-180 + 0.5 * lon_delta, 180, lon_delta)

    # create lat variable
    lat_delta = 180.0 / lat
    lat_variable = ds.createVariable('lat', 'f8', ('lat',), fill_value=FILL_VALUE)
    lat_variable.missing_value = FILL_VALUE
    lat_variable.standard_name = 'latitude'
    lat_variable.long_name = 'Latitude'
    lat_variable.units = 'degrees_north'
    lat_variable.axis = 'Y'
    lat_variable[:] = np.arange(90 - 0.5 * lat_delta, -90, -lat_delta)

    # create a data variable for each provided variable
    for variable_name, variable in variables.items():

        dimensions = ('time', 'lat', 'lon') if time is not None else ('lat', 'lon')
        var = ds.createVariable(variable_name, variable.dtype, dimensions,
                                fill_value=FILL_VALUE, compression='zlib')

        # set variable attributes
        for key, value in attrs.get(variable_name, {}).items():
            setattr(var, key, value)

        # set missing value
        var.missing_value = np.float32(FILL_VALUE)

        # set variable data
        var[:] = variable

    # set global attributes
    for key, value in attrs.get('global', {}).items():
        setattr(ds, key, value)

    return ds


def get_data_model(dataset: Dataset) -> str:
    """Get the data model of a NetCDF dataset.

    Args:
        dataset (Dataset): NetCDF4 Dataset object.

    Returns:
        String representing the data model (e.g., 'NETCDF4', 'NETCDF4_CLASSIC').
    """
    return dataset.data_model


def get_dimensions(dataset: Dataset) -> dict[str, int]:
    """Get dimensions from a NetCDF dataset.

    Args:
        dataset (Dataset): NetCDF4 Dataset object.

    Returns:
        Dictionary mapping dimension names to their sizes.
    """
    dimensions = {}
    for dimension_name, dimension in dataset.dimensions.items():
        dimensions[dimension_name] = dimension.size

    return dimensions


def get_variables(dataset: Dataset, convert: bool = False) -> dict[str, Any]:
    """Get variables and their attributes from a NetCDF dataset.

    Args:
        dataset (Dataset): NetCDF4 Dataset object.
        convert (bool): If True, convert numpy types to Python types (default: False).

    Returns:
        Dictionary mapping variable names to their attributes and dimensions.
    """
    variables = {}
    for variable_name, variable in dataset.variables.items():

        if convert:
            variables[variable_name] = {}
            for key, value in variable.__dict__.items():
                variables[variable_name][key] = convert_attribute(value)
        else:
            variables[variable_name] = variable.__dict__

        variables[variable_name]['dimensions'] = list(variable.dimensions)

    return variables


def get_global_attributes(dataset: Dataset, convert: bool = False) -> dict[str, Any]:
    """Get global attributes from a NetCDF dataset.

    Args:
        dataset (Dataset): NetCDF4 Dataset object.
        convert (bool): If True, convert numpy types to Python types (default: False).

    Returns:
        Dictionary of global attributes.
    """
    if convert:
        global_attributes = {}
        for key, value in dataset.__dict__.items():
            global_attributes[key] = convert_attribute(value)
    else:
        global_attributes = dataset.__dict__

    return global_attributes


def convert_attribute(value: Any) -> Any:
    """Convert numpy types to Python native types.

    Args:
        value (Any): Value to convert (may be numpy array, float, int, or other type).

    Returns:
        Converted value with Python native types.
    """
    if type(value) in LIST_TYPES:
        value = [convert_attribute(v) for v in value]
    elif type(value) in FLOAT_TYPES:
        value = float(value)
    elif type(value) in INT_TYPES:
        value = int(value)
    return value


def update_global_attributes(dataset: Dataset, set_attributes: dict | None = None,
                             delete_attributes: list | None = None) -> None:
    """Update global attributes of a NetCDF dataset.

    Args:
        dataset (Dataset): NetCDF4 Dataset object.
        set_attributes (dict): Dictionary of attributes to set or update.
        delete_attributes (list): List of attribute names to delete.
    """
    if delete_attributes is not None:
        for attr in dataset.__dict__:
            if attr in delete_attributes:
                dataset.delncattr(attr)

    if set_attributes is not None:
        for attr, value in set_attributes.items():
            dataset.setncattr(attr, value2string(value))


def value2string(value: Any) -> str:
    """Convert a value to string representation.

    Args:
        value (Any): Value to convert. Datetime objects get ISO format with 'Z' suffix.

    Returns:
        String representation of the value.
    """
    if isinstance(value, datetime):
        return value.isoformat() + 'Z'
    else:
        return str(value)
