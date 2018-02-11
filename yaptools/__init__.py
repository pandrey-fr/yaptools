# coding: utf-8

"""YAPTools - Yet Another Python Toolbox

This package provides with various utilitarian functions and classes.

Functions defined here:
    * alphanum_sort         : sort a list of strings, using integers
                              in a human-intuitive way.
    * check_type_validity   : check that a variable's type is as expected.
    * lazyproperty          : decorator providing a property's lazy evaluation.
    * pool_transform        : multiprocess an axis-wise computation
                              on a pandas Series or DataFrame.

Module defined here:
    * logger                : logging tools built upon the standard library.
"""

from ._utils import (
    alphanum_sort, _alphanum_key, check_type_validity, lazyproperty,
    pool_transform, _wrap_apply
)
from . import logger


__version__ = 0.1
