Java parser for Python

# Getting around

- `project\package` - main module path

- `project\tests`   - tests module path

- `pyproject.toml` - project metadata, with instructions for packaging

  See: https://hatch.pypa.io/latest/config/metadata/

- `requirements.txt` - package requirements to use the module

- `requirements-to-build.txt` - package requirements to build / package the module

Files and `javaload.py` and `javastream.py` are scripts to test a Java file quickly on whether it is loadable and streamable\*, respectively.

\*_To "stream" (-parse) a Java file is to handle shallow declarations and statements, only - not to load the file into an element tree. In fact, by implementation, it is a step that preceedes loading proper._

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
