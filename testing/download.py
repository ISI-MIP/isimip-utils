#!/usr/bin/env python3
from isimip_utils.tests import constants, helper


def main():
    download_datasets()
    download_protocol()


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


if __name__ == "__main__":
    main()
