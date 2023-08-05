Releases
========

Requirements
------------

Install `build` and `twine`

```
pip install build twine
```

Create `~/.pypirc`

```
[pypi]
username: ...
password: ...

[testpypi]
repository: https://test.pypi.org/legacy/
username: ...
password: ...
```

Prepare repo
------------

1) Ensure tests are passing.

2) Update version in `isimip_utils/__init__.py`.

3) Build `sdist` and `bdist_wheel`:

    ```
    python -m build
    ```

4) Check:

    ```
    twine check dist/*
    ```


Release on Test PyPI
--------------------

1) Upload with `twine` to Test PyPI:

    ```
    twine upload -r testpypi dist/*
    ```

2) Check at https://test.pypi.org/project/isimip-utils/.


Release on PyPI
---------------

1) Upload with `twine` to PyPI:

    ```
    twine upload dist/*
    ```

2) Check at https://pypi.org/project/isimip-utils/.


Create release on GitHub
------------------------

1) Commit local changes.

2) Push changes.

3) Create release on https://github.com/ISI-MIP/isimip-utils/releases).
