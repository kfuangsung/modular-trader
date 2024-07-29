from __future__ import annotations

from abc import ABC
from copy import deepcopy
from datetime import datetime
from typing import Iterable

from multimethod import multimethod
from talipp.input import Sampler, SamplingPeriodType
from talipp.ohlcv import OHLCV, OHLCVFactory

from framework_trader.common.type_aliases import DateOrDatetime, RealNumber


class BaseIndicator(ABC):
    def __init__(
        self,
        cache_size: int,
        sampling_period: SamplingPeriodType | None = None,
        input_indicator: BaseIndicator | None = None,
    ):
        self._cache_size = cache_size
        self._sampler = (
            Sampler(period_type=sampling_period) if sampling_period else None
        )
        self._previous_time = datetime.min
        self.calibrate_cache_size(input_indicator)

    cache_size = property(fget=lambda self: self._cache_size)
    sampler = property(fget=lambda self: self._sampler)
    previous_time = property(fget=lambda self: self._previous_time)

    @property
    def is_ready(self) -> bool:
        if len(self.output_values) > 0:
            return bool(self.output_values[-1])
        return False

    @property
    def value(self) -> RealNumber | None:
        if not self.is_ready:
            return
        return self.output_values[-1]

    @cache_size.setter
    def cache_size(self, value):
        self._cache_size = value

    @previous_time.setter
    def previous_time(self, value: DateOrDatetime):
        self._previous_time = value

    def copy(self):
        return deepcopy(self)

    def calibrate_cache_size(self, input_indicator):
        if input_indicator is not None:
            input_indicator.cache_size = max(
                self.cache_size, input_indicator.cache_size
            )

    def is_same_period(self, datetime: datetime | None) -> bool:
        if not self.sampler or not datetime:
            return False
        norm_prev_time = self.sampler._normalize(self.previous_time)
        norm_new_time = self.sampler._normalize(datetime)
        return norm_prev_time == norm_new_time

    def clean_cache(self) -> None:
        if self.cache_size:
            print(self.__class__.__name__, f"({self.cache_size})", "clean_cache")
            purge_size = max(0, len(self.input_values) - self.cache_size)
            self.purge_oldest(purge_size)

    def make_ohlcv(
        self,
        open: Iterable[RealNumber] | None = None,
        high: Iterable[RealNumber] | None = None,
        low: Iterable[RealNumber] | None = None,
        close: Iterable[RealNumber] | None = None,
        volume: Iterable[RealNumber] | None = None,
        datetime: Iterable[DateOrDatetime] | None = None,
    ) -> OHLCV:
        return OHLCVFactory.from_dict(
            {
                "open": open or [],
                "high": high or [],
                "low": low or [],
                "close": close or [],
                "volume": volume or [],
                "time": datetime or [],
            }
        )


class SingleInputMixin:
    @multimethod
    def ingest(
        self,
        close: RealNumber,
        datetime: DateOrDatetime | None = None,
        *args,
        **kwargs,
    ) -> None:
        if self.is_same_period(datetime):
            self.update(close)
        else:
            self.add(close)

        if datetime:
            self.previous_time = datetime

        self.clean_cache()

    @ingest.register
    def _(self, close: Iterable[RealNumber]):
        self.add(close)

    @ingest.register
    def _(
        self,
        close: Iterable[RealNumber],
        datetime: Iterable[DateOrDatetime],
    ):
        for c, d in zip(close, datetime):
            self.ingest(c, d)


class MultipleInputMixin:
    @multimethod
    def ingest(
        self,
        open: Iterable[RealNumber] | None,
        high: Iterable[RealNumber] | None,
        low: Iterable[RealNumber] | None,
        close: Iterable[RealNumber] | None,
        datetime: Iterable[DateOrDatetime] | None = None,
    ) -> None:
        # OHLCV use talipp's input sampling
        ohlcv = self.make_ohlcv(
            open=open, high=high, low=low, close=close, datetime=datetime
        )
        for value in ohlcv:
            self.add(value)
        self.clean_cache()

    @ingest.register
    def _(
        self,
        open: RealNumber | None,
        high: RealNumber | None,
        low: RealNumber | None,
        close: RealNumber | None,
        datetime: DateOrDatetime | None = None,
    ) -> None:
        return self.ingest(
            [open] if open is not None else None,
            [high] if high is not None else None,
            [low] if low is not None else None,
            [close] if close is not None else None,
            [datetime] if datetime is not None else None,
        )
