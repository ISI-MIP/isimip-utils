ISIMIP utils
============

[![Python Version](https://img.shields.io/badge/python->=3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/ISI-MIP/isimip-utils?style=flat)](https://github.com/ISI-MIP/isimip-utils/blob/main/LICENSE)
[![CI status](https://github.com/ISI-MIP/isimip-utils/actions/workflows/ci.yaml/badge.svg)](https://github.com/ISI-MIP/isimip-utils/actions/workflows/ci.yaml)
[![Latest release](https://img.shields.io/pypi/v/isimip-utils.svg?style=flat)](https://pypi.python.org/pypi/isimip-utils/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18937735.svg)](https://doi.org/10.5281/zenodo.18937735)

[ISIMIP](https://isimip.org) offers a framework for consistently projecting the impacts
of climate change across affected sectors and spatial scales. An international network
of climate-impact modellers contribute to a comprehensive and consistent picture of the
world under different climate-change scenarios.

This package contains various utility methods for use in custom scripts as well
as in different ISIMIP tools:

* [ISIMIP quality control](https://github.com/ISI-MIP/isimip-qc)
* [ISIMIP extraction and analysis](https://github.com/ISI-MIP/isimip-ea)
* [ISIMIP publisher](https://github.com/ISI-MIP/isimip-publisher)

The different methods are described are documented at <https://utils.isimip.org>.


Setup
-----

Using the package requires a running Python 3 on your system. The installation for different systems is covered
[here](https://utils.isimip.org/prerequisites/).

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

time = np.arrange(0, 365, dtype=np.float64)
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

Please also note our [examples page](https://utils.isimip.org/examples/) and the [API reference](https://utils.isimip.org/reference/).
