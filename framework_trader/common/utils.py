import json
import os
from typing import Any

from .constants import DEFAULT_CONFIG_PATH
from .enums import TradingMode


def get_config(path: os.PathLike = DEFAULT_CONFIG_PATH):
    """Loads a JSON configuration file.

    Args:
        path: The path to the configuration file. Defaults to
            DEFAULT_CONFIG_PATH.

    Returns:
        The loaded configuration as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    with open(path, "r") as f:
        return json.load(f)


def set_environ_config(cfg: dict[str, Any]):
    """
    Sets environment variables from the given configuration dictionary.

    Args:
        cfg: The configuration dictionary to set environment variables from.
    """
    for k, v in cfg.items():
        os.environ[k] = str(v)


def get_trading_mode() -> TradingMode:
    """
    Gets the trading mode as a TradingMode enum from the environment variable 'MODE'.

    If the variable is not set, it defaults to 'paper'.

    Returns:
        TradingMode: The trading mode.
    """
    return TradingMode(os.environ.get("MODE", "paper"))
