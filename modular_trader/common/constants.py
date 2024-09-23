import os
import pathlib

HOME: os.PathLike = pathlib.Path.home()
DEFAULT_DIR_NAME: str = ".framework_trader"
DEFAULT_DIR_PATH: os.PathLike = HOME.joinpath(DEFAULT_DIR_NAME)
DEFAULT_CONFIG_FILE: str = "config.json"
DEFAULT_LOG_FILE: str = "trader.log"
DEFAULT_RECORD_FILE: str = "record.json"
DEFAULT_FILE_ROTATION_SIZE_MB: int = 100
DEFAULT_CONFIG_PATH: os.PathLike = DEFAULT_DIR_PATH.joinpath(DEFAULT_CONFIG_FILE)
DEFAULT_LOG_PATH: os.PathLike = DEFAULT_DIR_PATH.joinpath(DEFAULT_LOG_FILE)
DEFAULT_RECORD_PATH: os.PathLike = DEFAULT_DIR_PATH.joinpath(DEFAULT_RECORD_FILE)
