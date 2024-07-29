from __future__ import annotations
from typing import TYPE_CHECKING
from .base import BaseIndicatorHandler
from pydantic.dataclasses import dataclass, Field
import enum

if TYPE_CHECKING:
    import pandas as pd


class TimePeriod(enum.Enum):
    MINUTE = enum.auto()
    DAY = enum.auto()


@dataclass
class AlpacaIndicatorHandler(BaseIndicatorHandler):
    # symbols: list[str]
    indicators: list[str]
    period: TimePeriod = Field(default=TimePeriod.DAY)
    # attr name in indicator
    # use name as symbol
    # e.g., SMA(name='SPY') -> hence use SPY data

    # mapper[name, non_init_indicator] : frozendict

    # save to Context
    # dict[symbol, dict[name, indicator]]

    def initialize(self):
        # find min cache_size -> use to get history
        self.data_length = 0

    def warmup(self, data: dict[str, pd.DataFrame]) -> None:
        # warmup from historical data
        # all indicator must accept OHLCV
        # or just pass *args, **kwargs
        pass

    def on_data_update(self, bar):
        # add / update data depending on bar's timestamp
        # use daily bars
        pass
