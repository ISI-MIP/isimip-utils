
import pytest

from isimip_utils.extractions import (
    compute_spatial_average,
    compute_temporal_average,
    concat_extraction,
    count_values,
    mask_bbox,
    mask_mask,
    select_bbox,
    select_period,
    select_point,
    select_time,
)
from isimip_utils.tests import constants, helper
from isimip_utils.xarray import get_attrs, open_dataset, set_attrs, write_dataset


@pytest.mark.parametrize('decode_cf', (True, False))
def test_select_time(decode_cf):
    date = constants.DATE
    date_specifiers = date.strftime('%Y%m%d')

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = (
        constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-time_')
                                                       .replace(constants.TAS_DATE_SPECIFIERS, date_specifiers)
    )
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = select_time(file_ds, date)
        write_dataset(ds, extraction_path)

    cdo_path = (
        constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-time-cdo_')
                                                       .replace(constants.TAS_DATE_SPECIFIERS, date_specifiers)
    )
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_select_period(decode_cf):
    start_date, end_date = constants.PERIOD
    date_specifiers = f'{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}'

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = (
        constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-period_')
                                                       .replace(constants.TAS_DATE_SPECIFIERS, date_specifiers)
    )
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = select_period(file_ds, start_date, end_date)
        write_dataset(ds, extraction_path)

    cdo_path = (
        constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-period-cdo_')
                                                       .replace(constants.TAS_DATE_SPECIFIERS, date_specifiers)
    )
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_select_point(decode_cf):
    lat, lon = constants.POINT

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point_')
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = select_point(file_ds, lat, lon)
        write_dataset(ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_select_point_concat(decode_cf):
    lat, lon = constants.POINT

    extraction_ds = None
    for path in constants.TAS_SPLIT_PATHS:
        dataset_path = constants.DATASETS_PATH / path

        with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
            ds = select_point(file_ds, lat, lon)
            extraction_ds = concat_extraction(extraction_ds, ds)

    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point_')
    extraction_path.unlink(missing_ok=True)

    write_dataset(extraction_ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_select_bbox(decode_cf):
    west, east, south, north = constants.BBOX

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox_')
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = select_bbox(file_ds, west, east, south, north)
        write_dataset(ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_select_bbox_concat(decode_cf):
    west, east, south, north = constants.BBOX

    extraction_ds = None
    for path in constants.TAS_SPLIT_PATHS:
        dataset_path = constants.DATASETS_PATH / path

        with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
            ds = select_bbox(file_ds, west, east, south, north)
            extraction_ds = concat_extraction(extraction_ds, ds)

    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox_')
    extraction_path.unlink(missing_ok=True)

    write_dataset(extraction_ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_mask_bbox(decode_cf):
    west, east, south, north = constants.BBOX

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-bbox_')
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = mask_bbox(file_ds, west, east, south, north)
        write_dataset(ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-bbox-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_mask_bbox_concat(decode_cf):
    west, east, south, north = constants.BBOX

    extraction_ds = None
    for path in constants.TAS_SPLIT_PATHS:
        dataset_path = constants.DATASETS_PATH / path

        with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
            ds = mask_bbox(file_ds, west, east, south, north)
            extraction_ds = concat_extraction(extraction_ds, ds)

    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-bbox_')
    extraction_path.unlink(missing_ok=True)

    write_dataset(extraction_ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-bbox-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_mask_mask(decode_cf):
    mask_path = constants.DATASETS_PATH / constants.LANDSEAMASK_PATH
    mask_ds = open_dataset(mask_path)

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-mask_')
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = mask_mask(file_ds, mask_ds)
        write_dataset(ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-mask-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_mask_mask_concat(decode_cf):
    mask_path = constants.DATASETS_PATH / constants.LANDSEAMASK_PATH
    mask_ds = open_dataset(mask_path)

    extraction_ds = None
    for path in constants.TAS_SPLIT_PATHS:
        dataset_path = constants.DATASETS_PATH / path

        with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
            ds = mask_mask(file_ds, mask_ds)
            extraction_ds = concat_extraction(extraction_ds, ds)

    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-mask_')
    extraction_path.unlink(missing_ok=True)

    write_dataset(extraction_ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_mask-mask-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_compute_spatial_average(decode_cf):
    gridarea_path = constants.SHARE_PATH / 'gridarea.nc'
    gridarea_ds = open_dataset(gridarea_path)

    west, east, south, north = constants.BBOX

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-mean_')
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        attrs = get_attrs(file_ds)
        ds = select_bbox(file_ds, west, east, south, north)
        ds = compute_spatial_average(ds, weights=gridarea_ds["cell_area"])
        ds = set_attrs(ds, attrs)
        write_dataset(ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-mean-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_compute_spatial_average_concat(decode_cf):
    gridarea_path = constants.SHARE_PATH / 'gridarea.nc'
    gridarea_ds = open_dataset(gridarea_path)

    west, east, south, north = constants.BBOX

    extraction_ds = None
    for path in constants.TAS_SPLIT_PATHS:
        dataset_path = constants.DATASETS_PATH / path

        with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
            attrs = get_attrs(file_ds)
            ds = select_bbox(file_ds, west, east, south, north)
            ds = compute_spatial_average(ds, weights=gridarea_ds["cell_area"])
            ds = set_attrs(ds, attrs)
            extraction_ds = concat_extraction(extraction_ds, ds)

    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-mean_')
    extraction_path.unlink(missing_ok=True)

    write_dataset(extraction_ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-mean-cdo_')
    helper.call(f'cdo diff {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_compute_temporal_average(decode_cf):
    west, east, south, north = constants.BBOX

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-map_')
    extraction_path.unlink(missing_ok=True)

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        attrs = get_attrs(file_ds)
        ds = select_bbox(file_ds, west, east, south, north)
        ds = compute_temporal_average(ds)
        ds = set_attrs(ds, attrs)
        write_dataset(ds, extraction_path)

    cdo_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-bbox-map-cdo_')
    helper.call(f'cdo diff,abslim=0.001 {extraction_path} {cdo_path}')


@pytest.mark.parametrize('decode_cf', (True, False))
def test_count_values(decode_cf):
    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = count_values(file_ds)
        assert (ds['tas'] == 720*360).all()


@pytest.mark.parametrize('decode_cf', (True, False))
def test_count_values_mask(decode_cf):
    west, east, south, north = constants.BBOX

    dataset_path = constants.DATASETS_PATH / constants.TAS_PATH

    with open_dataset(dataset_path, decode_cf=decode_cf) as file_ds:
        ds = mask_bbox(file_ds, west, east, south, north)
        ds = count_values(ds)
        assert (ds['tas'] == 400).all()
