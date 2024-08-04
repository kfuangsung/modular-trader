from __future__ import annotations

import enum
import warnings
from typing import TYPE_CHECKING, Generator, Mapping

from benedict import benedict
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from framework_trader.indicator.technical.base import BaseIndicator

from .base import BaseIndicatorHandler

if TYPE_CHECKING:
    import pandas as pd
    from alpaca.data.models.bars import Bar

    from framework_trader.universe import AssetUniverse


class Frequency(enum.Enum):
    MINUTE = enum.auto()
    DAY = enum.auto()


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid"))
class AlpacaIndicatorHandler(BaseIndicatorHandler):
    indicators: list[BaseIndicator] = Field(default_factory=list)
    frequency: Frequency = Field(default=Frequency.DAY)
    warmup_length: int | None = Field(default=None)
    _attached_indicators: benedict = Field(default_factory=lambda: benedict())

    attached_indicators = property(fget=lambda self: self._attached_indicators)
    symbols = property(fget=lambda self: list(self._attached_indicators.keys()))

    # save to Context
    # dict[symbol, dict[name, indicator]]

    def __post_init__(self) -> None:
        # find min cache_size -> use to get history
        self.warmup_length = self.warmup_length or max(
            [x.cache_size for x in self.indicators]
        )

    def __iter__(self) -> Generator[BaseIndicator, None, None]:
        return (x for x in self.indicators)

    @property
    def is_warmup(self) -> bool:
        return all(
            indicator.is_ready
            for indicator in self._attached_indicators.flatten().values()
        )

    def get(
        self, symbol: str, name: str | None = None
    ) -> BaseIndicator | Mapping[str, BaseIndicator] | None:
        symbol_indicators = self.attached_indicators.get(symbol, None)
        if symbol and name:
            return symbol_indicators.get(name, None)
        return symbol_indicators

    def init_indicator(self, universe: AssetUniverse) -> None:
        # add indicators for added symbol
        symbol: str
        for symbol in universe.added:
            indicator: BaseIndicator
            for indicator in self.indicators:
                key: str = f"{symbol}.{indicator.name}"
                if key in self._attached_indicators:
                    continue
                self._attached_indicators[key] = indicator.copy()

        # remove indicators for removed symbol
        self._attached_indicators.remove(list(universe.removed))

    def warmup(self, data: pd.DataFrame) -> None:
        # data -> MultiIndex [symbol, ...]
        # warmup from historical data
        data_symbols: list[str] = data.index.get_level_values(0).unique().to_list()
        symbol: str
        for symbol, it in self.attached_indicators.items():
            if symbol not in data_symbols:
                warnings.warn(f"Warm up indicator: {symbol} is not found in data.")
                continue
            indicator: BaseIndicator
            for indicator in it.values():
                if indicator.is_ready:
                    continue
                intput_data = (
                    data.loc[symbol, ["open", "high", "low", "close", "volume"]]
                    .reset_index()
                    .to_dict("list")
                )
                indicator.ingest(**intput_data)

    def update(self, bar: Bar) -> None:
        # if TimePeriod.MINUTE -> update in subscribe (minute) bars
        # if TimePeriod.DAY -> update in subscribe daily bars
        indicators = self.attached_indicators.get(bar.symbol, None)
        if indicators is None:
            warnings.warn(
                f"Update indicator: indicators for {bar.symbol} is not available."
            )
            return
        for indicator in indicators.values():
            indicator.ingest(
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
                timestamp=bar.timestamp,
            )
