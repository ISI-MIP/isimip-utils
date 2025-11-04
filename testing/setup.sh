#!/bin/bash

DATASETS_PATH=testing/datasets

DATASETS_FILES=(
    ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc
    ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2021_2030.nc
    ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2030_2040.nc
    ISIMIP3a/InputData/geo_conditions/landseamask/landseamask.nc
)

mkdir -p "${DATASETS_PATH}"

for FILE_PATH in "${DATASETS_FILES[@]}"; do
    # Create parent directories for the file
    mkdir -p "${DATASETS_PATH}/$(dirname "${FILE_PATH}")"
    wget -c "https://files.isimip.org/${FILE_PATH}" -O "${DATASETS_PATH}/${FILE_PATH}"
done

PROTOCOL_PATH=testing/protocol/output

PROTOCOL_FILES=(
    definitions/ISIMIP3a/OutputData/agriculture.json
    pattern/ISIMIP3a/OutputData/agriculture.json
    schema/ISIMIP3a/OutputData/agriculture.json
    tree/ISIMIP3a/OutputData/agriculture.json
)

mkdir -p "${PROTOCOL_PATH}"

for FILE_PATH in "${PROTOCOL_FILES[@]}"; do
    # Create parent directories for the file
    mkdir -p "${PROTOCOL_PATH}/$(dirname "${FILE_PATH}")"
    wget -c "https://protocol.isimip.org/${FILE_PATH}" -O "${PROTOCOL_PATH}/${FILE_PATH}"
done
