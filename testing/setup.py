#!/usr/bin/env python3
from isimip_utils.tests import constants, helper


def main():
    run_gridfile()
    run_seldate()

    run_select_time()
    run_select_period()
    run_select_point()
    run_select_bbox()
    run_select_bbox_mean()
    run_select_bbox_map()
    run_mask_bbox()
    run_mask_mask()


def download_datasets():
    constants.DATASETS_PATH.mkdir(parents=True, exist_ok=True)

    for path in [constants.LANDSEAMASK_PATH, constants.TAS_PATH, constants.YIELD_PATH]:
        file_path = constants.DATASETS_PATH / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://files.isimip.org/{path}"

        helper.call(f'wget -c {url} -O {file_path}')


def download_protocol():
    constants.PROTOCOL_PATH.mkdir(parents=True, exist_ok=True)

    for path in constants.PROTOCOL_PATHS:
        file_path = constants.PROTOCOL_PATH / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://protocol.isimip.org/{path}"

        helper.call(f'wget -c {url} -O {file_path}')


def run_gridfile():
    input_path = constants.DATASETS_PATH / constants.TAS_PATH
    output_path = constants.SHARE_PATH / 'gridarea.nc'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not output_path.exists():
        helper.call(f'cdo gridarea {input_path} {output_path}')


def run_seldate():
    input_path = constants.DATASETS_PATH / constants.TAS_PATH

    for start_date, end_date, specifiers in [
        ('2015-01-01', '2016-12-31', '2015_2016'),
        ('2017-01-01', '2018-12-31', '2017_2018'),
        ('2019-01-01', '2020-12-31', '2019_2020')
    ]:
        output_path = constants.DATASETS_PATH / constants.TAS_PATH.replace('2015_2020', specifiers)

        if not output_path.exists():
            helper.call(f'cdo -f nc4c -z zip_5 -L seldate,{start_date},{end_date} {input_path} {output_path}')


def run_select_time():
    date = constants.DATE

    path = constants.TAS_PATH

    input_path = constants.DATASETS_PATH / path

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-time-cdo_') \
                                                   .replace('2015_2020', '20180101')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not output_path.exists():
        helper.call(f'cdo -f nc4c -z zip_5 -L seldate,{date} {input_path} {output_path}')


def run_select_period():
    start_date, end_date = constants.PERIOD

    path = constants.TAS_PATH

    input_path = constants.DATASETS_PATH / path

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-period-cdo_') \
                                                   .replace('2015_2020', '2015')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not output_path.exists():
        helper.call(f'cdo -f nc4c -z zip_5 -L seldate,{start_date},{end_date} {input_path} {output_path}')


def run_select_point():
    ix, iy = constants.POINT_INDEX

    # add one since cdo is counting from 1!
    ix, iy = ix + 1, iy + 1

    for path in [constants.TAS_PATH, *constants.TAS_SPLIT_PATHS]:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-point-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            helper.call(f'cdo -f nc4c -z zip_5 -L -selindexbox,{ix},{ix},{iy},{iy} {input_path} {output_path}')


def run_select_bbox():
    west, east, south, north = constants.BBOX

    for path in [constants.TAS_PATH, *constants.TAS_SPLIT_PATHS]:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            helper.call(f'cdo -f nc4c -z zip_5 -L ' \
                        f'-sellonlatbox,{west},{east},{south},{north} {input_path} {output_path}')


def run_select_bbox_mean():
    west, east, south, north = constants.BBOX

    for path in [constants.TAS_PATH, *constants.TAS_SPLIT_PATHS]:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-mean-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            helper.call('cdo -f nc4c -z zip_5 -L -fldmean '
                        f'-sellonlatbox,{west},{east},{south},{north} {input_path} {output_path}')


def run_select_bbox_map():
    west, east, south, north = constants.BBOX

    for path in [constants.TAS_PATH, *constants.TAS_SPLIT_PATHS]:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-map-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            helper.call('cdo -f nc4c -z zip_5 -L timmean '
                        f'-sellonlatbox,{west},{east},{south},{north} {input_path} {output_path}')


def run_mask_bbox():
    west, east, south, north = constants.BBOX

    for path in [constants.TAS_PATH, *constants.TAS_SPLIT_PATHS]:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_mask-bbox-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            helper.call(f'cdo -f nc4c -z zip_5 -L '
                        f'-masklonlatbox,{west},{east},{south},{north} {input_path} {output_path}')


def run_mask_mask():
    mask_path = constants.DATASETS_PATH / constants.LANDSEAMASK_PATH

    for path in [constants.TAS_PATH, *constants.TAS_SPLIT_PATHS]:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_mask-mask-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            helper.call(f'cdo -f nc4c -z zip_5 -L -ifthen -selname,mask {mask_path} {input_path} {output_path}')


if __name__ == "__main__":
    main()
