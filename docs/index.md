ISIMIP utils
============

[ISIMIP](https://isimip.org) offers a framework for consistently projecting the impacts
of climate change across affected sectors and spatial scales. An international network
of climate-impact modellers contribute to a comprehensive and consistent picture of the
world under different climate-change scenarios.

Overview
--------

This package contains various utility methods for use in custom scripts as well
as in different ISIMIP tools:

* [ISIMIP quality control](https://github.com/ISI-MIP/isimip-qc)
* [ISIMIP quality assurance](https://github.com/ISI-MIP/isimip-qa)
* [ISIMIP publisher](https://github.com/ISI-MIP/isimip-publisher)

The following modules contain high-level method to extract data (e.g. aggregated time series of points, areas, shapes)
from global ISIMIP data sets and create gridded plots visualizing the data:

* [`isimip_utils.extractions`](api/extractions.md): Create extractions using [Xarray](https://docs.xarray.dev).
* [`isimip_utils.plot`](api/plot.md): Plotting utilities using [Vega-Altair](https://altair-viz.github.io).

Lower-level functions are provided to interact with the data sets and customize `xarray`, `pandas`, and `netcdf`
for ISIMIP conventions.

* [`isimip_utils.xarray`](api/xarray.md): Functions for working with `xarray` datasets.
* [`isimip_utils.netcdf`](api/netcdf.md): Functions to open and read NetCDF files using netCDF4.
* [`isimip_utils.pandas`](api/pandas.md): Pandas utilities for ISIMIP data processing.

Two modules focus on the interface to the [machine-readable ISIMIP protocol](https://protocol.isimip.org):

* [`isimip_utils.patterns`](api/patterns.md): Functions to fetch information from machine-actionable ISIMIP protocols.
* [`isimip_utils.protocol`](api/patterns.md): Functions to match file names and extract ISIMIP specifiers.

The remaining modules contain utility functions which are used by the other modules or by the ISIMIP tools mentioned above:

* [`isimip_utils.checksum`](api/checksum.md): Checksum computation utilities for file integrity verification.
* [`isimip_utils.cli`](api/cli.md): Command-line interface utilities for argument parsing and configuration.
* [`isimip_utils.config`](api/config.md): A `Settings` class for command-line interface utilities.
* [`isimip_utils.exceptions`](api/exceptions.md): Custom exceptions for ISIMIP tools.
* [`isimip_utils.fetch`](api/fetch.md): Functions to fetch files from urls or local paths.
* [`isimip_utils.files`](api/files.md): File search utilities with regex pattern matching.
* [`isimip_utils.parameters`](api/parameters.md): Utility functions for the work with parameters and placeholders.
* [`isimip_utils.utils`](api/utils.md): Additional utility functions.


Setup
-----

Using the package requires a running Python 3 on your system. The installation for different systems is covered
[here](https://github.com/ISI-MIP/isimip-utils/blob/master/docs/releases.md).

Unless you already use an environment manager (e.g. `conda` or `uv`), it is highly recommended to use a
[virtual environment](https://docs.python.org/3/library/venv.html), which can be created using:

```bash
python3 -m venv env
source env/bin/activate  # needs to be invoked in every new terminal session
```

The package itself can be installed via `pip`:

```bash
pip install isimip-utils
```

For a development setup, the repo should be cloned and installed in *editable* mode:

```bash
git clone git@github.com:ISI-MIP/isimip-utils
pip install -e isimip-utils
```


Usage
-----

Once installed, the modules can be used like any other Python library, e.g. in order to create a ISIMIP
compliant NetCDF file, you can use:

```python
from isimip_utils.xarray import init_dataset, write_dataset

time = np.arange(0, 365, dtype=np.float64)
var = np.ones((365, 360, 720), dtype=np.float32)

attrs={
    'global': {
        'contact': 'mail@example.com'
    },
    'var': {
        'standard_name': 'var',
        'long_name': 'Variable',
        'units': '1',
    }
}

# create an xarray.Dataset
ds = init_dataset(time=time, var=var, attrs=attrs)

# write the dataset as NetCDF file
write_dataset(ds, 'output.nc')
```

Please also note our page with additional [examples](examples.md) and the [API reference](api.md).
