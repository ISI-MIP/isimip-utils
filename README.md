ISIMIP utils
============

This package contains common functionality for different ISIMIP tools, namely:

* https://github.com/ISI-MIP/isimip-publisher
* https://github.com/ISI-MIP/isimip-qa
* https://github.com/ISI-MIP/isimip-qc

It comprises of:

* `isimip_utils.checksum`: Functions to compute the SHA-512 checksum of a file.
* `isimip_utils.config`: A settings class to combine input from `argparse`, the environment (via `python-dotenv`) and config files.
* `isimip_utils.exceptions`: Custom exceptions for ISIMIP tools.
* `isimip_utils.fetch`: Functions to fetch files from the machine-actionable ISIMIP protocols.
* `isimip_utils.netcdf`: Functions to open and read NetCDF files.
* `isimip_utils.patterns`: Functions to match the file names and extract the ISIMIP specifiers.
* `isimip_utils.utils`: Additional utility functions.


Setup
=====

The package can be installed via pip:

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
