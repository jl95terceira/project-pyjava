Java parser for Python

# Getting around

- `project\package` - main module path

- `project\tests`   - tests module path

- `pyproject.toml` - project metadata, with instructions for packaging

  See: https://hatch.pypa.io/latest/config/metadata/

- `requirements.txt` - package requirements to use the module

- `requirements-to-build.txt` - package requirements to build / package the module

# Build and install

Required:

- Python packages specified in `requirements-to-build.txt`, `pip`-installable via the following command.

  ```
  python -m pip install -r requirements-to-build.txt
  ```

To build / pack up, run the following command at the top directory.

```
python -m build
```

A `.whl` is generated at directory `dist` which can then be `pip`-installed like so.

```
python -m pip install dist\...whl
```
