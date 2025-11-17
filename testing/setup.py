#!/usr/bin/env python3
from pathlib import Path
from subprocess import check_call

from isimip_utils.extractions import concat_extraction, select_bbox, select_point
from isimip_utils.xarray import open_dataset, write_dataset

datasets_path = Path("testing/datasets")
extractions_path = Path("testing/extractions")
protocol_path = Path("testing/protocol/output")

mask_paths = [
    "ISIMIP3a/InputData/geo_conditions/landseamask/landseamask.nc"
]

dataset_paths = [
    "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc",
    "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2021_2030.nc",
    "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2031_2040.nc"
]

protocol_paths = [
    "definitions/ISIMIP3a/OutputData/agriculture.json",
    "pattern/ISIMIP3a/OutputData/agriculture.json",
    "schema/ISIMIP3a/OutputData/agriculture.json",
    "tree/ISIMIP3a/OutputData/agriculture.json"
]

bbox = (0, 10, -5, 5)
bbox_path = "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_bbox_daily.nc"  # noqa: E501

point = (52.395833, 13.061389)
point_path = "ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_point_daily.nc"  # noqa: E501

def main():
    # download_datasets()
    # download_protocol()
    create_extractions()


def download_datasets():
    datasets_path.mkdir(parents=True, exist_ok=True)

    for path in mask_paths + dataset_paths:
        file_path = datasets_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://files.isimip.org/{path}"

        check_call(['wget', '-c', url, '-O', file_path])


def download_protocol():
    protocol_path.mkdir(parents=True, exist_ok=True)

    for path in protocol_paths:
        file_path = protocol_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://protocol.isimip.org/{path}"

        check_call(['wget', '-c', url, '-O', file_path])


def create_extractions():
    west, east, south, north = bbox
    lat, lon = point

    for path in dataset_paths:
        file_path = datasets_path / path

        extraction_bbox = None
        extraction_point = None
        with open_dataset(file_path) as ds_file:
            ds_bbox = select_bbox(ds_file, west, east, south, north)
            extraction_bbox = concat_extraction(extraction_bbox, ds_bbox)

            ds_point = select_point(ds_file, lat, lon)
            extraction_point = concat_extraction(extraction_point, ds_point)

    write_dataset(extraction_bbox, extractions_path / bbox_path)
    write_dataset(extraction_point, extractions_path / point_path)

if __name__ == "__main__":
    main()
