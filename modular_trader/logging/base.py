from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru._logger import Logger


class BaseLogger:
    """
    Base class for loggers.

    Attributes:
        logger (loguru.Logger): The logger to use.
    """

    def __init__(self, logger: Logger = logger) -> None:
        """
        Initializes the logger.

        Args:
            logger (loguru.Logger, optional): The logger to use. Defaults to loguru.logger.
        """
        self.logger = logger

    def trace(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message at the trace level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.trace(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message at the debug level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message at the info level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.info(message, *args, **kwargs)

    def success(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message at the success level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.success(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message at the warning level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message at the error level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message at the critical level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """
        Logs an exception at the error level.

        Args:
            message (str): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.exception(message, *args, **kwargs)
