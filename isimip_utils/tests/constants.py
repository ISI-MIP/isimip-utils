from pathlib import Path

DATASETS_PATH = Path("testing/datasets")
EXTRACTIONS_PATH = Path("testing/extractions")
PLOTS_PATH = Path("testing/plots")
OUTPUT_PATH = Path("testing/output")

PROTOCOL_PATH = Path("testing/protocol/output")
SHARE_PATH = Path("testing/share")

LANDSEAMASK_PATH = "ISIMIP3a/InputData/geo_conditions/landseamask/landseamask.nc"

TAS_PATHS = [
    "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc",
    "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2021_2030.nc",
    "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2031_2040.nc"
]

YIELD_PATH = "ISIMIP3a/OutputData/agriculture/LPJmL/gswp3-w5e5/historical/lpjml_gswp3-w5e5_obsclim_2015soc_default_yield-mai-noirr_global_annual-gs_1901_2016.nc"  # noqa: E501

PROTOCOL_PATHS = [
    "definitions/ISIMIP3a/OutputData/agriculture.json",
    "pattern/ISIMIP3a/OutputData/agriculture.json",
    "schema/ISIMIP3a/OutputData/agriculture.json",
    "tree/ISIMIP3a/OutputData/agriculture.json"
]

PROTOCOL_LOCATIONS = ['testing/protocol']
PATTERN_PATH = 'ISIMIP3a/OutputData/agriculture.json'

DATE = '2018-01-01'
PERIOD = ('2017-01-01', '2018-12-31')

BBOX = (0, 10, -5, 5)

POINT = (52.395833, 13.061389)
POINT_INDEX = (386, 75)
