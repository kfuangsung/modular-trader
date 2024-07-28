from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru._logger import Logger


class BaseLogger:
    def __init__(self, logger: Logger = logger) -> None:
        self.logger = logger

    def trace(self, message: str, *args, **kwargs) -> None:
        self.logger.trace(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self.logger.info(message, *args, **kwargs)

    def success(self, message: str, *args, **kwargs) -> None:
        self.logger.success(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        self.logger.exception(message, *args, **kwargs)
