from pathlib import Path

from isimip_utils.fetch import fetch_pattern
from isimip_utils.patterns import find_files, match_dataset, match_dataset_path, match_file, match_file_path, match_path

protocol_locations = ['testing/protocol']
pattern_path = 'ISIMIP3a/OutputData/agriculture.json'

datasets_path = Path('testing/datasets')
dataset_path = Path('ISIMIP3a/OutputData/agriculture/LPJmL/gswp3-w5e5/historical/lpjml_gswp3-w5e5_obsclim_2015soc_default_yield-mai-noirr_global_annual-gs')  # noqa: E501
file_path = Path('ISIMIP3a/OutputData/agriculture/LPJmL/gswp3-w5e5/historical/lpjml_gswp3-w5e5_obsclim_2015soc_default_yield-mai-noirr_global_annual-gs_1901_2016.nc')  # noqa: E501

additional_paths = [
    Path("ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc"),
    Path("ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2021_2030.nc"),
    Path("ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2031_2040.nc")
]

path_specifiers = {
    'simulation_round': 'ISIMIP3a',
    'product': 'OutputData',
    'sector': 'agriculture',
    'period': 'historical'
}

dataset_specifiers = {
    'model': 'lpjml',
    'climate_forcing': 'gswp3-w5e5',
    'climate_scenario': 'obsclim',
    'soc_scenario': '2015soc',
    'sens_scenario': 'default',
    'variable': 'yield',
    'crop': 'mai',
    'irrigation': 'noirr',
    'region': 'global',
    'time_step': 'annual-gs'
}

file_specifiers = {
    **dataset_specifiers,
    'start_year': 1901,
    'end_year': 2016,
}


def test_match_dataset_path():
    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_dataset_path(pattern, datasets_path / dataset_path)
    assert str(path) == str(dataset_path)
    assert specifiers == {**path_specifiers, **dataset_specifiers}


def test_match_file_path():
    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_file_path(pattern, datasets_path / file_path)
    assert str(path) == str(file_path)
    assert specifiers == {**path_specifiers, **file_specifiers}


def test_match_dataset():
    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_dataset(pattern, datasets_path / dataset_path)
    assert str(path) == dataset_path.name
    assert specifiers == dataset_specifiers


def test_match_file():
    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_file(pattern, datasets_path / file_path)
    assert str(path) == file_path.name
    assert specifiers == file_specifiers


def test_match_path():
    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_path(pattern, datasets_path / file_path)
    assert str(path) == str(file_path)
    assert specifiers == {**path_specifiers, **file_specifiers}


def test_match_path_specifiers_map():
    pattern = fetch_pattern(pattern_path, protocol_locations)
    pattern['specifiers_map'] = {
        'global': 'spam'
    }
    path, specifiers = match_path(pattern, datasets_path / file_path)
    assert str(path) == str(file_path)
    assert specifiers == {**path_specifiers, **file_specifiers, 'region': 'spam'}


def test_find_files():
    pattern = fetch_pattern(pattern_path, protocol_locations)
    files = [file_path.name] + [path.name for path in additional_paths]
    result = find_files(pattern['file'], files)
    assert len(result)
    assert result == [(
        Path(file_path.name),
        file_specifiers
    )]
