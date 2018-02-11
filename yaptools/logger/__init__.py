# coding: utf-8

"""Logging tools, built upon those from the logging standard library.

Classes defined:
    * Logger       : logging.Logger child, adding a handler builder.
    * LoggedObject : abstract class for serializable logged objects.
    * LevelsFilter : logging filter allowing precise levels to pass.

Function defined:
    * loggedmethod : decorator to log LoggedObject methods' exceptions.
"""

from ._logger import (
    Logger, LoggedObject, LevelsFilter, loggedmethod, LOGGING_LEVELS
)
