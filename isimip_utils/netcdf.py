from datetime import datetime

import numpy as np

from netCDF4 import Dataset

LIST_TYPES = [np.ndarray]
FLOAT_TYPES = [np.float32, np.float64]
INT_TYPES = [np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32, np.int64, np.uint64]


def open_dataset_read(file_path):
    return Dataset(file_path, 'r')


def open_dataset_write(file_path):
    return Dataset(file_path, 'r+')


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
