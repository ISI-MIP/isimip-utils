"""
Requirements:
    pip install isimip-utils[netcdf,xarray]
"""

from pathlib import Path

from isimip_utils.cli import setup_logs
from isimip_utils.extractions import concat_extraction, select_point
from isimip_utils.xarray import load_dataset, write_dataset

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
output_template = 'gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_{specifier}_daily.nc'

points = [
    (52.395833, 13.061389, 'potsdam'),
]

extractions = {}
for file_name in files:
    # load the dataset completely in memory
    with load_dataset(datasets_path / file_name) as file_ds:
        # loop over points, select time series and concat to extraction ds
        for lat, lon, specifier in points:
            ds = select_point(file_ds, lat, lon)
            extractions[specifier] = (
                concat_extraction(extractions.get(specifier), ds)
            )

# write extraction ds for every region
for _, _, specifier in points:
    extraction_path = output_path / output_template.format(specifier=specifier)
    write_dataset(extractions[specifier], extraction_path)
