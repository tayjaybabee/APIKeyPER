"""
log_engine
----------
Author: Taylor-Jayde
Date: Today's Date

This module provides logging utilities tailored for the APIKeyPER application. It establishes a flexible logging mechanism
with support for both console and file outputs, featuring rich, colored console logs using the Rich library. The module
also incorporates a Singleton design pattern for the Logger class, ensuring consistent logging behavior across the
application.

Furthermore, the module provides a meta-class 'Loggable' which can be inherited by other classes to instantly equip them
with logging capabilities.

Key components:
    - Logger: A Singleton class responsible for managing application logging.
    - Loggable: A meta-class providing logging capabilities to the classes that inherit from it.

Dependencies:
    - logging: Standard library module for event logging.
    - RichHandler from rich.logging: Provides rich, colored output for console logs.
    - inspect: Standard library module for introspecting live objects.
    - apikeyper.__about__: Module providing metadata about the APIKeyPER application.
    - apikeyper.log_engine.helpers: Helper functions for the logging engine.
"""

import inspect
import logging
from rich.logging import RichHandler
from apikeyper.__about__ import __PROG__ as PROG_NAME
from apikeyper.log_engine.helpers import (
    translate_to_logging_level,
    clean_module_name,
    CustomFormatter,
)


DEFAULT_LOGGING_LEVEL = logging.DEBUG


class Logger:
    """
    A Singleton class responsible for managing the logging mechanisms of the application.
    It ensures consistent logging behavior across different parts of the application by
    maintaining single instances of loggers with specific names. The class supports
    logging to both the console (with colored output) and a file.

    Attributes:
        - instances (dict): Keeps track of logger instances to implement the Singleton pattern.
    """

    instances = {}

    def __new__(cls, name, *args, **kwargs):
        """
        Creates a new instance or returns an existing instance of the Logger class for the provided name.
        This method ensures that only one instance of Logger with a given name exists, implementing the Singleton pattern.

        Parameters:
            name (str): The name of the logger.

        Returns:
            Logger: An instance of the Logger class.
        """

        if name not in cls.instances:
            instance = super(Logger, cls).__new__(cls)
            cls.instances[name] = instance
            return instance
        return cls.instances[name]

    def __init__(
        self,
        name,
        console_level=DEFAULT_LOGGING_LEVEL,
        file_level=logging.DEBUG,
        filename="app.log",
    ):
        """
        Initializes a logger instance. Sets up console and file handlers and establish logging levels.

        Parameters:
            name (str):
                The name of the logger.

            console_level (logging level object, optional):
                The logging level for the console. Defaults to DEBUG.
                Must be a member of logging module's set of level constants (like logging.INFO or logging.DEBUG).

            file_level (logging level object, optional):
                The logging level for the file. Defaults to DEBUG.
                Must be a member of logging module's set of level constants (like logging.INFO or logging.DEBUG).

            filename (str, optional): The name of the log file. Defaults to 'app.log'.
        """
        if not hasattr(self, "logger"):
            self.__name = name
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.DEBUG)
            self.__console_level = console_level
            self.filename = filename
            self.__file_level = file_level or DEFAULT_LOGGING_LEVEL

            # Remove existing handlers
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            # Prevent log records from being passed to the handlers of ancestor loggers.
            self.logger.propagate = False

            self.set_up_console()
            self.set_up_file()
            self.children = []

    def set_up_console(self):
        """
        Configures and attaches a console handler to the logger. This method uses the RichHandler to produce
        colored and formatted console outputs.
        """

        console_handler = RichHandler(
            show_level=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        formatter = CustomFormatter(
            "[green][bold][%(name)s][bold][/green] - %(message)s"
        )

        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.__console_level)
        self.logger.addHandler(console_handler)

    def set_up_file(self):
        """
        Configures and attaches a file handler to the logger. This ensures that log messages are also written
        to a specified file.
        """

        file_handler = logging.FileHandler(self.filename)
        file_handler.setLevel(self.__file_level)
        formatter = CustomFormatter(
            "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def set_level(self, console_level=None, file_level=None):
        """
        Updates the logging levels for both the console and file handlers. If provided, also updates child loggers.

        Parameters:
            console_level (logging level object, optional):
                The console logging level. Defaults to None.

            file_level (logging level object, optional):
                The file logging level. Defaults to None.
        """

        if console_level is not None:
            self.logger.handlers[0].setLevel(console_level)
            for child in self.children:
                child.set_level(console_level=console_level)

        if file_level is not None:
            self.logger.handlers[1].setLevel(file_level)
            for child in self.children:
                child.set_level(file_level=file_level)

    def get_child(self, name=None, console_level=None, file_level=None):
        console_level = console_level or DEFAULT_LOGGING_LEVEL

        # Get the stack frame of the caller
        caller_frame = inspect.stack()[1]

        # If no name is provided, use the name of the calling function/method/class
        if name is None:
            name = caller_frame.function

        # Check if the caller is a class or a function/method
        caller_self = caller_frame.frame.f_locals.get("self", None)

        # Determine the separator
        separator = ":" if caller_self and hasattr(caller_self, name) else "."
        child_logger_name = f"{self.logger.name}{separator}{name}"

        # Check if child logger already exists
        for child in self.children:
            if child.logger.name == child_logger_name:
                return child

        # If child logger doesn't exist, create a new one
        child_logger = Logger(child_logger_name, console_level, file_level)
        self.children.append(child_logger)
        return child_logger

    def get_child_names(self) -> list[str]:
        """
        Fetches the names of all child loggers associated with this logger instance.

        Returns:
            list of str:
                 A list containing the names of all child loggers.
        """

        return [child.logger.name for child in self.children]

    def find_child_by_name(
        self,
        name: str,
    ):
        names = self.get_child_names()


LOG_DEVICE = Logger(PROG_NAME, DEFAULT_LOGGING_LEVEL)
MOD_LOG_DEVICE = LOG_DEVICE.get_child("log_engine")
MOD_LOGGER = MOD_LOG_DEVICE.logger
MOD_LOGGER.debug(f"Started logger for {__name__}.")

add_child = LOG_DEVICE.get_child


import inspect


def _get_parent_logging_device():
    """
    Determines the parent logging device by inspecting the caller's log_device or parent_log_device attribute.

    Returns:
        Logger: The parent logging device.
    """
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals
    print(caller_locals)

    if "logger" in caller_locals:
        return caller_locals["logger"]
    elif "parent_log_device" in caller_locals:
        return caller_locals["parent_log_device"]
    else:
        raise ValueError("Unable to determine the parent logging device.")


class Loggable:
    """
    A metaclass to enhance classes with logging capabilities. Classes that inherit from
    'Loggable' can instantly access a logger without manually setting it up. This logger
    is derived from a parent logger, ensuring consistent logging behavior and hierarchy.

    Attributes:
        - log_device: The logger device associated with the instance of the class.
    """

    def __init__(self, parent_log_device=None, **kwargs):
        self.parent_log_device = parent_log_device
        self.__log_name = self.__class__.__name__
        if self.parent_log_device is not None:
            self.__log_device = self.parent_log_device.get_child(
                self.__class__.__name__
            )
        else:
            self.__log_device = _get_parent_logging_device().get_child(
                self.__class__.__name__
            )

    @property
    def log_device(self):
        return self.__log_device

    @log_device.setter
    def log_device(self, new):
        if not isinstance(new, Logger):
            raise TypeError('log_device must be of type "Logger"')

        self.__log_device = new

    def create_child_logger(self, name=None, override=False):
        """
        Creates and returns a child logger of this object's logger.

        Parameters:
            name (str, optional): The name of the child logger.
                If not provided, the name of the calling function is used.
            override (bool, optional): A flag to override the membership check. Defaults to False.

        Returns:
            Logger: An instance of the Logger class that represents the child logger.
        """
        if not override:
            self.__is_member__()

        if name is None:
            name = inspect.stack()[1][
                3
            ]  # Get the name of the calling function if no name is provided

        return self.log_device.get_child(name)

    def __is_member__(self):
        """
        Checks whether the caller of this method is a member of the same class.

        Raises:
            PermissionError: If the caller of this method is not a member of the same class.
        """
        log_device = self.log_device.get_child("__is_member__")
        log = log_device.logger

        current_frame = inspect.currentframe()
        log.debug(f"Current frame: {current_frame}")

        caller_frame = current_frame.f_back
        log.debug(f"Caller frame: {caller_frame}")

        caller_self = caller_frame.f_locals.get("self", None)
        log.debug(f"Caller self: {caller_self}")

        log.debug("Checking if caller is a member of this class...")
        if not isinstance(caller_self, self.__class__):
            raise PermissionError(
                "Access denied.\n"
                f"Method can only be accessed by members of the same class. {caller_self.__class__.__name__} is not such a member"
            )

        log.debug(f"Access granted to {caller_self.__class__.__name__}")
