#!/usr/bin/env python3
from isimip_utils.tests import constants, helper


def main():
    download_datasets()
    download_protocol()
    run_gridfile()
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

    for path in [constants.LANDSEAMASK_PATH, *constants.TAS_PATHS, constants.YIELD_PATH]:
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
    input_path = constants.DATASETS_PATH / constants.TAS_PATHS[0]
    output_path = constants.SHARE_PATH / 'gridarea.nc'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    helper.call(f'cdo gridarea {input_path} {output_path}')


def run_select_time():
    date = constants.DATE

    path = constants.TAS_PATHS[0]

    input_path = constants.DATASETS_PATH / path

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-time-cdo_') \
                                                   .replace('2015_2020', '20180101')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    helper.call(f'cdo -f nc4c -z zip_5 -L seldate,{date} {input_path} {output_path}')


def run_select_period():
    start_date, end_date = constants.PERIOD

    path = constants.TAS_PATHS[0]

    input_path = constants.DATASETS_PATH / path

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-period-cdo_') \
                                                   .replace('2015_2020', '2017_2018')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    helper.call(f'cdo -f nc4c -z zip_5 -L seldate,{start_date},{end_date} {input_path} {output_path}')


def run_select_point():
    ix, iy = constants.POINT_INDEX

    # add one since cdo is counting from 1!
    ix, iy = ix + 1, iy + 1

    output_paths = []
    for path in constants.TAS_PATHS:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-point-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        output_paths.append(str(output_path))

        helper.call(f'cdo -f nc4c -z zip_5 -L -selindexbox,{ix},{ix},{iy},{iy} {input_path} {output_path}')

    input_paths = ' '.join(output_paths)

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-point-cdo_') \
                                                   .replace('2031_2040', '2015_2040')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    helper.call(f'cdo -f nc4c -z zip_5 cat {input_paths} {output_path}')


def run_select_bbox():
    west, east, south, north = constants.BBOX

    output_paths = []
    for path in constants.TAS_PATHS:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        output_paths.append(str(output_path))

        helper.call(f'cdo -f nc4c -z zip_5 -L -sellonlatbox,{west},{east},{south},{north} {input_path} {output_path}')

    input_paths = ' '.join(output_paths)

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-cdo_') \
                                                   .replace('2031_2040', '2015_2040')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    helper.call(f'cdo -f nc4c -z zip_5 cat {input_paths} {output_path}')


def run_select_bbox_mean():
    west, east, south, north = constants.BBOX

    output_paths = []
    for path in constants.TAS_PATHS:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-mean-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        output_paths.append(str(output_path))

        helper.call('cdo -f nc4c -z zip_5 -L -fldmean ' \
                    f'-sellonlatbox,{west},{east},{south},{north} {input_path} {output_path}')

    input_paths = ' '.join(output_paths)

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-mean-cdo_') \
                                                   .replace('2031_2040', '2015_2040')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    helper.call(f'cdo -f nc4c -z zip_5 cat {input_paths} {output_path}')


def run_select_bbox_map():
    west, east, south, north = constants.BBOX

    for path in constants.TAS_PATHS:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_select-bbox-map-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        helper.call('cdo -f nc4c -z zip_5 -L timmean ' \
                    f'-sellonlatbox,{west},{east},{south},{north} {input_path} {output_path}')


def run_mask_bbox():
    west, east, south, north = constants.BBOX

    output_paths = []
    for path in constants.TAS_PATHS:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_mask-bbox-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        output_paths.append(str(output_path))

        helper.call(f'cdo -f nc4c -z zip_5 -L -masklonlatbox,{west},{east},{south},{north} {input_path} {output_path}')

    input_paths = ' '.join(output_paths)

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_mask-bbox-cdo_') \
                                                   .replace('2031_2040', '2015_2040')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    helper.call(f'cdo -f nc4c -z zip_5 cat {input_paths} {output_path}')


def run_mask_mask():
    mask_path = constants.DATASETS_PATH / constants.LANDSEAMASK_PATH

    output_paths = []
    for path in constants.TAS_PATHS:
        input_path = constants.DATASETS_PATH / path

        output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_mask-mask-cdo_')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        output_paths.append(str(output_path))

        helper.call(f'cdo -f nc4c -z zip_5 -L -ifthen -selname,mask {mask_path} {input_path} {output_path}')

    input_paths = ' '.join(output_paths)

    output_path = constants.EXTRACTIONS_PATH / path.replace('_global_', '_mask-mask-cdo_') \
                                                   .replace('2031_2040', '2015_2040')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    helper.call(f'cdo -f nc4c -z zip_5 cat {input_paths} {output_path}')


if __name__ == "__main__":
    main()
