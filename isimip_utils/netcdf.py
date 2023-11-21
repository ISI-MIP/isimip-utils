from datetime import datetime

import numpy as np
from netCDF4 import Dataset

FILL_VALUE = 1e+20
LIST_TYPES = [np.ndarray]
FLOAT_TYPES = [np.float32, np.float64]
INT_TYPES = [np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32, np.int64, np.uint64]


def open_dataset_read(file_path):
    return Dataset(file_path, 'r')


def open_dataset_write(file_path):
    return Dataset(file_path, 'r+')


def init_dataset(file_path, diskless=False, lon=720, lat=360, time=True,
                 time_unit='days since 1601-1-1 00:00:00',
                 time_calendar='proleptic_gregorian', **variables):
    ds = Dataset(file_path, 'w', format='NETCDF4_CLASSIC', diskless=diskless)

    if time is not None and time is not False:
        ds.createDimension('time', None)

    ds.createDimension('lon', lon)
    ds.createDimension('lat', lat)

    if time is not None:
        time_variable = ds.createVariable('time', 'f8', ('time',))
        time_variable.standard_name = 'time'
        time_variable.long_name = 'Time'
        time_variable.units = time_unit
        time_variable.calendar = time_calendar

        if isinstance(time, np.ndarray):
            time_variable[:] = time

    lon_variable = ds.createVariable('lon', 'f8', ('lon',))
    lon_variable.standard_name = 'longitude'
    lon_variable.long_name = 'Longitude'
    lon_variable.units = 'degrees_east'
    lon_variable.axis = 'X'
    lon_variable[:] = np.arange(-179.75, 180.25, 0.5)

    lat_variable = ds.createVariable('lat', 'f8', ('lat',))
    lat_variable.standard_name = 'latitude'
    lat_variable.long_name = 'Latitude'
    lat_variable.units = 'degrees_north'
    lat_variable.axis = 'Y'
    lat_variable[:] = np.arange(89.75, -90.25, -0.5)

    for variable_name, variable_dict in variables.items():
        long_name = variable_dict.get('long_name')
        dtype = variable_dict.get('dtype', 'f8')
        dimensions = variable_dict.get('dimensions', ('time', 'lat', 'lon'))
        units = variable_dict.get('units')

        if variable_name:
            variable = ds.createVariable(variable_name, dtype, dimensions,
                                         fill_value=FILL_VALUE, compression='zlib')
            variable.missing_value = FILL_VALUE
            variable.standard_name = variable_name
            if long_name:
                variable.long_name = long_name
            if units:
                variable.units = units

    return ds


def get_data_model(dataset):
    return dataset.data_model


def get_dimensions(dataset):
    dimensions = {}
    for dimension_name, dimension in dataset.dimensions.items():
        dimensions[dimension_name] = dimension.size

    return dimensions


def get_variables(dataset, convert=False):
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


def get_global_attributes(dataset, convert=False):
    if convert:
        global_attributes = {}
        for key, value in dataset.__dict__.items():
            global_attributes[key] = convert_attribute(value)
    else:
        global_attributes = dataset.__dict__

    return global_attributes


def convert_attribute(value):
    if type(value) in LIST_TYPES:
        value = [convert_attribute(v) for v in value]
    elif type(value) in FLOAT_TYPES:
        value = float(value)
    elif type(value) in INT_TYPES:
        value = int(value)
    return value


def update_global_attributes(dataset, set_attributes={}, delete_attributes=[]):
    for attr in dataset.__dict__:
        if attr in delete_attributes:
            dataset.delncattr(attr)

    for attr, value in set_attributes.items():
        dataset.setncattr(attr, value2string(value))


def value2string(value):
    if isinstance(value, datetime):
        return value.isoformat() + 'Z',
    else:
        return str(value)
