import os

from loguru import logger
from loguru._logger import Logger
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from framework_trader.common.constants import (
    DEFAULT_FILE_ROTATION_SIZE_MB,
    DEFAULT_LOG_PATH,
)

from .base import BaseLogger


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid"))
class TradingLogger(BaseLogger):
    logger: Logger = Field(default=logger)
    file_path: os.PathLike = Field(default=DEFAULT_LOG_PATH)
    rotation_size_mb: int = Field(default=DEFAULT_FILE_ROTATION_SIZE_MB)
    retention_days: int = Field(default=None)

    def __post_init__(self):
        rotation = f"{self.rotation_size_mb} MB" if self.rotation_size_mb else None
        retention = f"{self.retention_days} days" if self.retention_days else None
        self.logger.add(self.log_file_path, rotation=rotation, retention=retention)
