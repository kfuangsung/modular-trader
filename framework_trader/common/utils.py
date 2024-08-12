import json
import os
from typing import Any

from .constants import DEFAULT_CONFIG_PATH
from .enums import TradingMode


def get_config(path: os.PathLike = DEFAULT_CONFIG_PATH):
    with open(path, "r") as f:
        return json.load(f)


def set_environ_config(cfg: dict[str, Any]):
    for k, v in cfg.items():
        os.environ[k] = str(v)


def get_trading_mode() -> TradingMode:
    return TradingMode(os.environ.get("MODE", "paper"))
