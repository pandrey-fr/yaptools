# Yet Another Python Toolbox (YAPTools)

YAPTools is a Python package grouping utilitarian functions and classes
which I commonly use in various Python projects. As any toolbox conceived
by any programmer, it may provide with useful tools for some people, and
yet seem utterly useless to others. I mainly publish this toolbox as a
dependency for other open-source projects which I hope may be useful to other
people.

YAPTools currently includes:
- `alphanum_sort`, a string-sorting algorithm handling numbers in a
   human-intuitive way (created by Dave Koelle).

- `check_type_validity`, a function checking that a variable is of desired
   type and raising custom exceptions if not.

- `import_from_string`, a function to run imports based on objects' names.

- `instantiate`, a function to recursively (re)instantiate any object based on
   serializable initialization parameters.

- `lazyproperty`, a decorator enabling the lazy evaluation of a class property.

- `logger`, a module implementing tools over those of the `logging` standard
   library, noticeably including:
   - `LevelsFilter`, a `logging.Filter` allowing only messages of specific
      levels to pass.

   - `LoggedObject`, an abstract class providing with serializable logging tools,
      meaning they can be used parallely by multiprocessed instances of an object.

   - `Logger`, a variant of `logging.Logger` with a simplified way to set handlers.

- `onetimemethod`, a decorator preventing a method to be called more than once.

- `pool_transform`, a function to easily distribute on multiple CPU cores
   an axis-wise tranformation of a `pandas.DataFrame` or `pandas.Series`.


### User installation

**Dependencies**

- Python 3 (>= 3.3) &nbsp;&nbsp; -- &nbsp;&nbsp; Python 2.x is **not** supported.
- Pandas (>= 0.20) &nbsp;&nbsp; -- &nbsp;&nbsp; third-party package
  distributed under BSD 3-Clause License.

**Downloading a copy of the repository**

To copy the project on your local machine, provided you have Git installed,
simply clone the repository with the following command:

```
git clone https://github.com/pandrey-fr/yaptools.git
```

**Installing the package**

**Warning**: It is advised to procede to the installation in a virtual
environment. To learn how to set up such an environment, please refer to
the `venv` [documentation](https://docs.python.org/3/library/venv.html).

To install YAPTools as a `yaptools` package, use the `setup.py` file in
the main folder :

```
python setup.py install
```

### Contributing

If you feel like some modification of YAPTools might be useful to others,
please open an issue on Github, and/or submit a Pull Request with your
modifications.

### License

YAPTools is distributed under the MIT License.
