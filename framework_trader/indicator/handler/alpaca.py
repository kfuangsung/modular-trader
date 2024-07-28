from __future__ import annotations
from typing import TYPE_CHECKING
from .base import BaseIndicatorHandler
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class AlpacaIndicatorHandler(BaseIndicatorHandler):
    symbols: list[str]
    indicators: list

    def initialize(self):
        self.data_length = 0

    def warmup(self, data: dict[str, pd.DataFrame]) -> None:
        pass

    def on_update(self, bar):
        pass
