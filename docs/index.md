ISIMIP utils
============

Overview
--------

This package contains common functionality for different ISIMIP tools, namely:

* https://github.com/ISI-MIP/isimip-publisher
* https://github.com/ISI-MIP/isimip-qa
* https://github.com/ISI-MIP/isimip-qc

It comprises of:

* [`isimip_utils.checksum`](api/checksum.md): Functions to compute the SHA-512 checksum of a file.
* [`isimip_utils.cli`](api/cli.md): Command-line interface utilities for argument parsing and configuration.
* [`isimip_utils.config`](api/config.md): A settings class to combine input from `argparse`, the environment (via `python-dotenv`) and config files.
* [`isimip_utils.decorators`](api/decorators.md): Decorators including a cached property implementation.
* [`isimip_utils.exceptions`](api/exceptions.md): Custom exceptions for ISIMIP tools.
* [`isimip_utils.extractions`](api/extractions.md): Data extraction and manipulation utilities for xarray datasets.
* [`isimip_utils.fetch`](api/fetch.md): Functions to fetch files from the machine-actionable ISIMIP protocols.
* [`isimip_utils.files`](api/files.md): File search utilities with regex pattern matching.
* [`isimip_utils.netcdf`](api/netcdf.md): Functions to open and read NetCDF files using netCDF4.
* [`isimip_utils.pandas`](api/pandas.md): DataFrame utilities for ISIMIP data processing.
* [`isimip_utils.patterns`](api/patterns.md): Functions to match file names and extract ISIMIP specifiers.
* [`isimip_utils.plot`](api/plot.md): Plotting utilities using Altair for data visualization.
* [`isimip_utils.utils`](api/utils.md): Additional utility functions.
* [`isimip_utils.xarray`](api/xarray.md): Functions for working with xarray datasets.


Setup
-----

Working on the package requires a running Python3 on your system. Installing those prerequisites is covered [here](https://github.com/ISI-MIP/isimip-utils/blob/master/docs/releases.md).

The package itself can be installed via pip:

```
pip install isimip-utils
```

The package can also be installed directly from GitHub:

```
pip install git+https://github.com/ISI-MIP/isimip-utils
```

For a development setup, the repo should be cloned and installed in *editable* mode:

```
git clone git@github.com:ISI-MIP/isimip-utils
pip install -e isimip-utils
```
