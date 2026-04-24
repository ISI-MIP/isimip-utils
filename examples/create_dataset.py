"""
Requirements:
    pip install isimip-utils[netcdf,xarray]
"""

from pathlib import Path

import numpy as np

from isimip_utils.cli import setup_logs
from isimip_utils.xarray import init_dataset, write_dataset

setup_logs('INFO')

dataset_path = Path('output') / 'dataset.nc'

# create example time axis
time = np.arange(0, 100, dtype=np.float64)

# create example variable
var = np.ones((100, 360, 720), dtype=np.float32)

# create global and variable attributes
# lon, lat and time attributes will be set automatically
attrs={
    'global': {
        'contact': 'mail@example.com'
    },
    'var': {
        'standard_name': 'var',
        'long_name': 'Variable',
        'units': '1',
    }
}

# create and write xarray dataset
ds = init_dataset(time=time, var=var, attrs=attrs)
write_dataset(ds, dataset_path)
