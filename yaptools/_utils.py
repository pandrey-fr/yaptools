# codin: utf-8

"""Set of generic (i.e. non-contextual) utilitarian functions.

In the source code, objects are sorted by alphabetical order, with
private elements following the public ones they first serve in.
"""

import re
import inspect
import functools
import multiprocessing

import pandas as pd


def alphanum_sort(string_list):
    """Sort a list of strings using the alphanum algorithm.

    Dave Koelle's Alphanum algorithm sorts names containing integer
    in a more human-intuitive way than the usual Ascii-based way.

    E.g. sorting ['2', '1', '10'] results in ['1', '2', '10'],
         whereas built-in sorted() results in ['1', '10', '2'].
    """
    check_type_validity(string_list, list, 'string_list')
    if not all(isinstance(string, str) for string in string_list):
        raise TypeError('The provided list contains non-string elements.')
    return sorted(string_list, key=_alphanum_key)


def _alphanum_key(string):
    """Parse a string into string and integer components."""
    parity = int(string[0] in '0123456789')
    return [
        int(x) if i % 2 != parity else x
        for i, x in enumerate(re.split('([0-9]+)', string)[parity:])
    ]


def check_type_validity(instance, valid_types, varname):
    """Raise a TypeError if a given variable instance is not of expected type.

    instance    : instance whose type to check
    valid_types : expected type (or tuple of types)
    varname     : variable name to use in the exception's message
    """
    if isinstance(valid_types, type):
        valid_types = (valid_types,)
    elif isinstance(valid_types, list):
        valid_types = tuple(valid_types)
    if float in valid_types and int not in valid_types:
        valid_types = (*valid_types, int)
    if not isinstance(instance, valid_types):
        raise TypeError(
            "Expected '%s' to be of type %s, not %s" % (
                varname, ' or '.join(map(lambda x: x.__name__, valid_types)),
                type(instance).__name__
            )
        )


def lazyproperty(method):
    """Decorator for methods defining an attribute's one-time evaluation.

    Once the attribute's value has been evaluated (i.e. after it is called
    for the first time), this value is returned without further evaluation
    at each new call.

    It is however possible to delete the value using `del`, so that it is
    re-evaluated on the next call (but not on the following ones).

    Example:
    >>> class Foo:
    ...     def __init__(self, x):
    ...         self.x = x
    ...     @lazyproperty
    ...     def bar(self):
    ...         return self.x
    ...
    >>> foo = Foo(0)
    >>> foo.bar
    0
    >>> foo.x = 1
    >>> foo.bar
    0
    >>> del foo.bar
    >>> foo.bar
    1
    """
    name = method.__name__
    def getter(instance, *args, **kwargs):
        """Return the property's value, evaluating it if needed."""
        if name not in instance.__dict__.keys():
            instance.__dict__[name] = method(instance, *args, **kwargs)
        return instance.__dict__[name]
    def deleter(instance):
        """Delete the property's value."""
        instance.__dict__.pop(name, None)
    doc = getattr(method, '__doc__', None)
    if doc is None:
        doc = 'Lazy property %s.' % method.__name__
    return property(getter, fdel=deleter, doc=doc)


def pool_transform(
        series_or_dataframe, function, pool_size,
        apply_func=False, aggregate=None, **kwargs
    ):
    """Multiprocess a row-wise computation on a pandas Series or DataFrame.

    function   : function that either takes a pd.Series or pd.DataFrame
                 as input, or is to be applied to one such object's contents
    pool_size  : number of workers to divide work between (positive int)
    apply_func : whether to call `series_or_dataframe.apply(function)` instead
                 of `function(series_or_dataframe)` (bool, default False)
    aggregate  : optional results aggregation function (when pool_size > 1)
                 that takes a list of partial results as input

    Any valid keyword argument of the applied function may be passed.
    """
    check_type_validity(
        series_or_dataframe, (pd.Series, pd.DataFrame), 'series_or_dataframe'
    )
    if not inspect.isfunction(function):
        raise TypeError("Invalid 'function' type: %s." % type(function))
    check_type_validity(pool_size, int, 'pool_size')
    if pool_size <= 0:
        raise ValueError("Invalid 'pool_size' value: negative integer.")
    check_type_validity(apply_func, bool, 'apply_func')
    if not aggregate is None or inspect.isfunction(aggregate):
        raise TypeError(
            "Expected 'aggregate' to be either None or a function, not %s."
            % type(aggregate).__name__
        )
    function = (
        functools.partial(_wrap_apply, func=function, **kwargs)
        if apply_func else functools.partial(function, **kwargs)
    )
    pool_size = min(pool_size, len(series_or_dataframe))
    if pool_size < 2:
        return function(series_or_dataframe)
    with multiprocessing.Pool(pool_size) as pool:
        n_rows = len(series_or_dataframe)
        chunk_size = n_rows // pool_size + int(n_rows % pool_size > 0)
        chunks = (
            series_or_dataframe.iloc[i:i + chunk_size]
            for i in range(0, n_rows, chunk_size)
        )
        results = pool.map(function, chunks)
    return aggregate(results) if aggregate is not None else results


def _wrap_apply(series_or_dataframe, func, **kwargs):
    """Wrap a pandas.Series or pandas.DataFrame apply(func, **kwargs) call."""
    return series_or_dataframe.apply(func, **kwargs)
