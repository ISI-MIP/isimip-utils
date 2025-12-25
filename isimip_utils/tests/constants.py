from datetime import date
from pathlib import Path

DATASETS_PATH = Path("testing/datasets")
EXTRACTIONS_PATH = Path("testing/extractions")
PLOTS_PATH = Path("testing/plots")
OUTPUT_PATH = Path("testing/output")

PROTOCOL_PATH = Path("testing/protocol/output")
SHARE_PATH = Path("testing/share")

LANDSEAMASK_PATH = "ISIMIP3a/InputData/geo_conditions/landseamask/landseamask.nc"

TAS_PATH = "ISIMIP3a/InputData/climate/atmosphere/obsclim/global/daily/" \
           "historical/20CRv3-ERA5/20crv3-era5_obsclim_tas_global_daily_2021_2021.nc"

TAS_DATE_SPECIFIERS = '2021_2021'

TAS_SPLIT_PERIOD =  (
    (date(2021, 1, 1), date(2021, 4, 30)),
    (date(2021, 5, 1), date(2021, 8, 31)),
    (date(2021, 9, 1), date(2021, 12, 31))
)
TAS_SPLIT_PATHS = [
    TAS_PATH.replace(TAS_DATE_SPECIFIERS, f'{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}')
    for start_date, end_date in TAS_SPLIT_PERIOD
]

YIELD_PATH = "ISIMIP3a/OutputData/agriculture/LPJmL/gswp3-w5e5/historical/" \
             "lpjml_gswp3-w5e5_obsclim_2015soc_default_yield-mai-noirr_global_annual-gs_1901_2016.nc"

PROTOCOL_PATHS = [
    "definitions/ISIMIP3a/OutputData/agriculture.json",
    "pattern/ISIMIP3a/OutputData/agriculture.json",
    "schema/ISIMIP3a/OutputData/agriculture.json",
    "tree/ISIMIP3a/OutputData/agriculture.json"
]

PROTOCOL_LOCATIONS = ['testing/protocol']
PATTERN_PATH = 'ISIMIP3a/OutputData/agriculture.json'

DATE = date(2021, 1, 1)
PERIOD = date(2021, 4, 1), date(2021, 9, 30)

BBOX = (0, 10, -5, 5)

POINT = (52.395833, 13.061389)
POINT_INDEX = (386, 75)
