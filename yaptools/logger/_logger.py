# coding: utf-8

"""Logging tools, built upon those from the logging standard library."""

import logging
import functools
import inspect
import os

from yaptools import check_type_validity


LOGGING_LEVELS = {
    'debug': logging.DEBUG, 'info': logging.INFO,
    'warning': logging.WARNING, 'warn': logging.WARN,
    'error': logging.ERROR, 'fatal': logging.FATAL,
    'critical': logging.CRITICAL
}


class Logger(logging.Logger):
    """Class adding a handler builder to logging.Logger."""

    def __init__(self, name=None, folder='.', level=1, config=None):
        """Initialize the logger and set up its handlers.

        name     : optional logger name (str, default None)
        folder   : reference folder to write log files to (default '.')
        level    : minimum and default logging level (int, default 1)
        config   : optional list of dict specifying handlers' configuration
                   (see below for details -- default: stream handler)

        Each dict in handlers may contain the following keys:

        kind   : kind of handler (required, either 'stream', 'file' or 'queue')
        path   : file path ('file' kind) or queue object ('queue' kind)
        levels : optional list of record levels (int or str) to accept
        """
        # Check basic arguments validity and primarily setup the logger.
        check_type_validity(name, (str, type(None)), 'name')
        check_type_validity(level, int, 'level')
        level = max(0, level)
        super().__init__(name, level)
        # Set up and assign the folder attribute.
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif not os.path.isdir(folder):
            raise ValueError("'%s' is not a folder." % folder)
        self.folder = os.path.abspath(folder)
        # Set up and assign the config attribute.
        check_type_validity(config, (list, type(None)), 'config')
        if config is None:
            config = [{'kind': 'stream'}]
        self.handlers_config = config
        # Set up the logger's handlers based on its handlers_config attribute.
        self._levels = LOGGING_LEVELS.copy()
        self._levels['default'] = self.level
        if not self.hasHandlers():
            self.setup()

    def setup(self):
        """Set up the logger's handlers."""
        for config in self.handlers_config:
            handler = self.build_handler(**config)
            self.addHandler(handler)

    def build_handler(self, kind, path=None, levels=None):
        """Return a logging handler of given configuration.

        kind   : kind of handler, either 'stream', 'file' or 'queue'
        path   : None, file path or queue (depending on kind)
        levels : optional restrictive list of record levels to accept
        """
        # Set up the handler.
        if kind == 'stream':
            handler = logging.StreamHandler()
        elif kind == 'file':
            assert path is not None, 'FileHandler requires a path.'
            handler = logging.FileHandler(path, mode='a')
        elif kind == 'queue':
            assert hasattr(path, 'put_nowait'), 'invalid Queue to handle.'
            handler = logging.handlers.QueueHandler(path)
        else:
            raise ValueError('Invalid handler kind: "%s"' % kind)
        # Add formatter and optional levels filter.
        if levels is not None:
            levels_filter = LevelsFilter(levels)
            handler.addFilter(levels_filter)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s :{} %(message)s'.format(
                '' if self.name == '' else ' %s :' % self.name
            )
        ))
        return handler

    def log(self, level, msg, *args, **kwargs):
        """Log 'msg' with the severity 'level' (int or str).

        See logging.log documentation for additional options.
        """
        if isinstance(level, str):
            level = self._levels.get(level, self.level)
        elif not isinstance(level, int):
            warning = (
                "Invalid 'level' argument passed to 'log': %s (type %s)."
                % (level, type(level).__name__)
            )
            super().log(logging.WARNING, warning)
            level = self.level
        super().log(level, msg, *args, **kwargs)


class LoggedObject:
    """Abstract class implementing logging methods.

    A class inheriting from this one will (and must) be dotted with
    a yaptools.logger.Logger 'logger' attribute which can be used
    through the shortcut method 'log' and  whose default settings
    can be set by overriding the '_default_logger' property.

    The 'logger' attribute will also be made serializable, meaning
    that multiprocessed instances of inheriting classes will be able
    to commonly log through it.

    Usage:
    >>> class Foo(LoggedObject):
    ...     def __init__(self, x, logger=None):
    ...         self.x = x
    ...         super().__init__(logger)
    ...     @property
    ...     def _default_logger(self):  # Overriding this method is optional.
    ...         # optionally define a name, folder, level and/or configuration
    ...         return Logger(name, folder, level, config)
    ...
    >>> foo = Foo(42)
    >>> foo.log(foo.x, level='info')
    <asctime> : <foo.logger name> : 42
    """

    def __init__(self, logger=None):
        """Initialize the logger attribute."""
        if logger is None:
            self.logger = self._default_logger
        elif isinstance(logger, Logger):
            self.logger = logger
        else:
            raise TypeError("Invalid 'logger' type: %s." % type(logger))

    @property
    def _default_logger(self):
        """Return a default logger. Meant to be overriden."""
        return Logger()

    def __getstate__(self):
        """On pickling, remove the logger system."""
        statedict = self.__dict__.copy()
        statedict['_logger_name'] = self.logger.name
        statedict['_logger_folder'] = self.logger.folder
        statedict['_logger_config'] = self.logger.handlers_config.copy()
        del statedict['logger']
        return statedict

    def __setstate__(self, statedict):
        """On unpickling, restore the logger system."""
        self.logger = Logger(
            statedict['_logger_name'], statedict['_logger_folder'],
            statedict['_logger_config']
        )
        del statedict['_logger_name']
        del statedict['_logger_folder']
        del statedict['_logger_config']
        self.__dict__.update(statedict)

    def log(self, msg, level='default'):
        """Log a given `msg` string with the severity `level` (str or int)."""
        self.logger.log(level, msg)

    def log_exception(self, exception, level='error'):
        """Log a given exception with a given severity level."""
        msg = '%s: %s.' % (type(exception), ';'.join(map(str, exception.args)))
        self.log(msg, level)


def loggedmethod(method):
    """Decorator for LoggedObject methods, ensuring exceptions logging.

    Whenever an exception is raised by a method this function decorates,
    its details are logged through the object's `log` method at 'error'
    level before it is raised again.

    This is useful when unexpected exceptions may be raised in a context
    where they will not interrupt execution but need to be notified.

    Usage:
    >>> class Foo(LoggedObject):
    ...     @loggedmethod
    ...     def bar(self, x):
    ...         if not isinstance(x, str);
    ...             raise TypeError('Expected "x" to be a str.')
    ...         self.log(x)
    ...
    >>> foo = Foo()
    >>> foo.bar('Some string.')
    <asctime> : Some string.
    >>> foo.bar(42)
    <asctime> : TypeError at `Foo.bar`: Expected "x" to be a str.
    TypeError: Expected "x" to be a str.
    """
    if 'self' not in inspect.signature(method).parameters.keys():
        raise RuntimeError(
            "Attempt at decorating a function with no 'self' argument "
            + "using '@logged_method'."
        )
    @functools.wraps(method)
    def logged_method(self, *args, **kwargs):
        """Wrapped method ensuring exceptions logging before raising."""
        try:
            return method(self, *args, **kwargs)
        except Exception as exception:
            method_name = getattr(method, '__qualname__', method.__name__)
            msg = "%s at '%s': %s" % (
                type(exception).__name__, method_name,
                ';'.join(map(str, exception.args))
            )
            self.log(msg=msg, level='error')
            raise exception
    return logged_method


class LevelsFilter(logging.Filter):
    """Logging filter setting an exhaustive set of passing levels."""

    def __init__(self, levels):
        """Set up levels to filter out, provided as a list of int or str."""
        super().__init__()
        if isinstance(levels, (int, str)):
            levels = [levels]
        check_type_validity(levels, list, 'levels')
        self.levels = [self.format_level(level) for level in levels]

    @staticmethod
    def format_level(level):
        """Return the integer value of a given logging level (int or str)."""
        if isinstance(level, int):
            return level
        elif isinstance(level, str):
            if level in LOGGING_LEVELS.keys():
                return LOGGING_LEVELS[level]
            else:
                raise KeyError("Invalid level name: '%s'." % level)
        else:
            raise TypeError(
                "Expected 'level' to be of type int or str, not %s."
                % type(level).__name__
            )

    def filter(self, record):
        """Return whether a given record passes the filter or not."""
        return record.levelno in self.levels
