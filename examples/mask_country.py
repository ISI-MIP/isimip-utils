"""
Requirements:
    pip install isimip-utils[netcdf,xarray]
"""

from pathlib import Path

from isimip_utils.cli import setup_logs
from isimip_utils.extractions import mask_mask
from isimip_utils.xarray import open_dataset, write_dataset

setup_logs('INFO')

datasets_path = Path('datasets')

files = [
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2021_2030.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2031_2040.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2041_2050.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2051_2060.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2061_2070.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2071_2080.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2081_2090.nc',
    'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2091_2100.nc',
]


output_path = Path('output')

# open binary country mask
mask_name = 'countrymasks-binary_30arcmin.nc'
mask_ds = open_dataset(datasets_path / mask_name)
mask_var = 'm_GRL'
mask_region = '_grl_'

for file_name in files:
    masked_path = output_path / file_name.replace('_global_', mask_region)

    with open_dataset(datasets_path / file_name) as ds:
        masked_ds = mask_mask(ds, mask_ds, mask_var=mask_var, inverse=True)
        write_dataset(masked_ds, masked_path)
