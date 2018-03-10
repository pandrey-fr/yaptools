# coding: utf-8

"""YAPTools - Yet Another Python Toolbox

This package provides with various utilitarian functions and classes.

Functions defined here:
    * alphanum_sort       : sort a list of strings ordering integers properly.
    * check_type_validity : check that a variable's type is as expected.
    * import_from_string  : import any object based on its full name.
    * instanciate         : instanciate an object from serializable components.
    * lazyproperty        : decorator providing a property's lazy evaluation.
    * pool_transform      : multiprocess a pandas object axis-wise computation.
    * onetimemethod       : prevent a method from being called more than once.

Module defined here:
    * logger              : logging tools built upon the standard library.
"""

from ._utils import (
    alphanum_sort, _alphanum_key, check_type_validity, import_from_string,
    instanciate, lazyproperty, pool_transform, _wrap_apply, onetimemethod
)
from . import logger


__version__ = '0.1.2'
