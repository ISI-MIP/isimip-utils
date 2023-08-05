ISIMIP utils
============

[![Latest release](https://shields.io/github/v/release/ISI-MIP/isimip-utils)](https://github.com/ISI-MIP/isimip-utils/releases)
[![PyPI Release](https://img.shields.io/pypi/v/isimip-utils)](https://pypi.org/project/isimip-utils/)
[![Python Version](https://img.shields.io/badge/python->=3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/ISI-MIP/django-datacite/blob/master/LICENSE)

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
