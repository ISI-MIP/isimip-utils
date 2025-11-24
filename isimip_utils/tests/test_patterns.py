from pathlib import Path

from isimip_utils.fetch import fetch_pattern
from isimip_utils.patterns import find_files, match_dataset, match_dataset_path, match_file, match_file_path, match_path
from isimip_utils.tests import constants

protocol_locations = ['testing/protocol']

pattern_path = 'ISIMIP3a/OutputData/agriculture.json'

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
    dataset_path = Path(constants.YIELD_PATH.replace('_1901_2016.nc', ''))

    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_dataset_path(pattern, constants.DATASETS_PATH / dataset_path)

    assert str(path) == str(dataset_path)
    assert specifiers == {**path_specifiers, **dataset_specifiers}


def test_match_file_path():
    file_path = Path(constants.YIELD_PATH)

    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_file_path(pattern, constants.DATASETS_PATH / file_path)

    assert str(path) == str(file_path)
    assert specifiers == {**path_specifiers, **file_specifiers}


def test_match_dataset():
    dataset_path = Path(constants.YIELD_PATH.replace('_1901_2016.nc', ''))

    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_dataset(pattern, constants.DATASETS_PATH / dataset_path)

    assert str(path) == dataset_path.name
    assert specifiers == dataset_specifiers


def test_match_file():
    file_path = Path(constants.YIELD_PATH)

    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_file(pattern, constants.DATASETS_PATH / file_path)

    assert str(path) == file_path.name
    assert specifiers == file_specifiers


def test_match_path():
    file_path = Path(constants.YIELD_PATH)

    pattern = fetch_pattern(pattern_path, protocol_locations)
    path, specifiers = match_path(pattern, constants.DATASETS_PATH / constants.YIELD_PATH)

    assert str(path) == str(file_path)
    assert specifiers == {**path_specifiers, **file_specifiers}


def test_match_path_specifiers_map():
    file_path = Path(constants.YIELD_PATH)

    pattern = fetch_pattern(pattern_path, protocol_locations)
    pattern['specifiers_map'] = {
        'global': 'spam'
    }
    path, specifiers = match_path(pattern, constants.DATASETS_PATH / file_path)

    assert str(path) == str(file_path)
    assert specifiers == {**path_specifiers, **file_specifiers, 'region': 'spam'}


def test_find_files():
    file_path = Path(constants.YIELD_PATH)
    files = [file_path.name] + [file_path.name.replace('_global_', s) for s in ('a', 'b', 'c')]

    pattern = fetch_pattern(pattern_path, protocol_locations)
    result = find_files(pattern['file'], files)
    assert len(result)
    assert result == [(
        Path(file_path.name),
        file_specifiers
    )]
