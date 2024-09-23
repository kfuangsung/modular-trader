from __future__ import annotations

from abc import ABC
from copy import deepcopy
from datetime import datetime
from typing import Iterable

from multimethod import multidispatch
from talipp.input import Sampler, SamplingPeriodType
from talipp.ohlcv import OHLCV, OHLCVFactory

from modular_trader.common.type_aliases import DateOrDatetime, RealNumber


class BaseIndicator(ABC):
    """Base class for all indicators.

    Attributes:
        cache_size (int): The number of last values to keep in memory.
        sampler (Sampler | None): The sampler used to sample the input data.
        input_indicator (BaseIndicator | None): The input indicator.
        previous_time (datetime | None): The time of the last value.
        name (str | None): The name of the indicator.
    """

    def __init__(
        self,
        cache_size: int,
        sampling_period: SamplingPeriodType | None = None,
        input_indicator: BaseIndicator | None = None,
        name: str | None = None,
    ):
        """
        Initialize the indicator.

        Args:
            cache_size (int): The number of last values to keep in memory.
            sampling_period (SamplingPeriodType | None): The sampling period.
            input_indicator (BaseIndicator | None): The input indicator.
            name (str | None): The name of the indicator.
        """
        self._cache_size = cache_size
        self._sampler = (
            Sampler(period_type=sampling_period) if sampling_period else None
        )
        self._input_indicator = input_indicator
        self._previous_time = datetime.min
        self._name = name or self.__class__.__name__
        self.calibrate_cache_size(input_indicator)

    cache_size = property(fget=lambda self: self._cache_size)
    sampler = property(fget=lambda self: self._sampler)
    previous_time = property(fget=lambda self: self._previous_time)
    name = property(fget=lambda self: self._name)

    def __repr__(self) -> str:
        """Return a string representation of the indicator.

        The string representation of the indicator is of the form
        "<IndicatorName>(name=<name>, value=<value>)" where <IndicatorName>
        is the name of the indicator class, <name> is the name of the
        indicator, and <value> is the current value of the indicator.

        Returns:
            str: The string representation of the indicator.
        """
        return f"{self.__class__.__name__}(name={self.name}, value={self.value})"

    def __str__(self) -> str:
        """Return a string representation of the indicator.

        The string representation of the indicator is of the form
        "<IndicatorName>(name=<name>, value=<value>)" where <IndicatorName>
        is the name of the indicator class, <name> is the name of the
        indicator, and <value> is the current value of the indicator.

        Returns:
            str: The string representation of the indicator.
        """
        return self.__repr__()

    @property
    def is_ready(self) -> bool:
        """Check if the indicator has calculated a valid value.

        The indicator is considered ready when it has calculated a valid
        value. This is useful for checking if the indicator has finished its
        warmup period.

        Returns:
            bool: True if the indicator has calculated a valid value, False otherwise.
        """
        if len(self.output_values) > 0:
            return bool(self.output_values[-1])
        return False

    @property
    def value(self) -> RealNumber | None:
        """
        Get the current value of the indicator.

        The current value of the indicator is the last value calculated
        by the indicator. If the indicator has not finished its warmup
        period, None is returned.

        Returns:
            RealNumber | None: The current value of the indicator, or None if the indicator has not finished its warmup period.
        """
        if not self.is_ready:
            return
        return self.output_values[-1]

    @cache_size.setter
    def cache_size(self, value):
        """
        Set the cache size of the indicator.

        The cache size is the number of last calculated values to keep in memory.
        It is used to optimize the calculation of indicators by avoiding the
        recalculation of values that have already been calculated.

        Args:
            value (int): The cache size. Must be greater than 0.
        """
        self._cache_size = value

    @previous_time.setter
    def previous_time(self, value: DateOrDatetime):
        """
        Set the previous time of the indicator.

        The previous time is the time of the previous calculated value.
        It is used to determine if the indicator should recalculate its value
        when new data is available.

        Args:
            value (DateOrDatetime): The new previous time.
        """
        self._previous_time = value

    def copy(self):
        """
        Create a deep copy of the indicator.

        Returns a deep copy of the indicator, which is a new indicator instance
        with the same configuration and values as the original indicator.

        Returns:
            BaseIndicator: A deep copy of the indicator.
        """
        return deepcopy(self)

    def calibrate_cache_size(self, input_indicator):
        """
        Calibrate the cache size of the input indicator.

        If the input indicator is not None, the cache size of the input
        indicator is set to the maximum of the cache size of the indicator
        and the cache size of the input indicator. This ensures that the
        input indicator has enough cache size to be used by the indicator.

        Args:
            input_indicator (BaseIndicator | None): The input indicator.
        """
        if input_indicator is not None:
            input_indicator.cache_size = max(
                self.cache_size, input_indicator.cache_size
            )

    def is_same_period(self, timestamp: DateOrDatetime | None) -> bool:
        """
        Check if the timestamp is in the same period as the previous time.

        Args:
            timestamp (DateOrDatetime | None): The timestamp to check.

        Returns:
            bool: True if the timestamp is in the same period as the previous time, False otherwise.

        Note:
            This method is used to determine if the indicator should recalculate its value
            when new data is available. If the timestamp is in the same period as the
            previous time, the indicator will not recalculate its value.
        """
        if not self.sampler or not timestamp:
            return False
        norm_prev_time = self.sampler._normalize(self.previous_time)
        norm_new_time = self.sampler._normalize(timestamp)
        return norm_prev_time == norm_new_time

    def clean_cache(self) -> None:
        """
        Clean the cache by purging the oldest values.

        If the cache size is set, the method purges the oldest values from the
        cache until the cache size is reached. This ensures that the cache does
        not grow indefinitely.

        Note:
            This method is called automatically by the framework when the
            indicator is updated.
        """
        if self.cache_size:
            # print(self.__class__.__name__, f"({self.cache_size})", "clean_cache")
            purge_size = max(0, len(self.input_values) - self.cache_size)
            self.purge_oldest(purge_size)

    def make_ohlcv(
        self,
        open: Iterable[RealNumber] | None = None,
        high: Iterable[RealNumber] | None = None,
        low: Iterable[RealNumber] | None = None,
        close: Iterable[RealNumber] | None = None,
        volume: Iterable[RealNumber] | None = None,
        timestamp: Iterable[DateOrDatetime] | None = None,
    ) -> OHLCV:
        """
        Create an OHLCV object from the given values.

        Args:
            open: The open prices.
            high: The high prices.
            low: The low prices.
            close: The close prices.
            volume: The volumes.
            timestamp: The timestamps.

        Returns:
            OHLCV: The created OHLCV object.
        """
        return OHLCVFactory.from_dict(
            {
                "open": open or [],
                "high": high or [],
                "low": low or [],
                "close": close or [],
                "volume": volume or [],
                "time": timestamp or [],
            }
        )

    def ingest(
        self,
        open: RealNumber | Iterable[RealNumber] | None,
        high: RealNumber | Iterable[RealNumber] | None,
        low: RealNumber | Iterable[RealNumber] | None,
        close: RealNumber | Iterable[RealNumber] | None,
        volume: RealNumber | Iterable[RealNumber] | None = None,
        timestamp: RealNumber | Iterable[DateOrDatetime] | None = None,
    ):
        """
        Ingest values into the indicator.

        If an input indicator is set, the values will be ingested into the input indicator.
        Otherwise, the values will be ingested into this indicator.

        Args:
            open: The open prices.
            high: The high prices.
            low: The low prices.
            close: The close prices.
            volume: The volumes.
            timestamp: The timestamps.
        """
        if self._input_indicator is not None:
            return self._input_indicator.ingest(
                open=open,
                high=high,
                low=low,
                close=close,
                volume=volume,
                timestamp=timestamp,
            )
        else:
            return self._ingest(
                open=open,
                high=high,
                low=low,
                close=close,
                volume=volume,
                timestamp=timestamp,
            )


class SingleInputMixin:
    """
    Mixin for indicators that ingest a single value.

    Provides a default implementation for the `_ingest` method that handles
    ingesting a single value into the indicator.

    The `_ingest` method is called by the `ingest` method of the indicator, and
    is responsible for updating the indicator with the ingested value.

    The default implementation of `_ingest` checks if the timestamp of the
    ingested value is in the same period as the previous time, and if so,
    updates the indicator with the new value. If the timestamp is not in the
    same period, the indicator is reset with the new value.

    The default implementation of `_ingest` also calls the `clean_cache` method
    of the indicator to purge the oldest values from the cache.

    Attributes:
        None

    Methods:
        _ingest: Ingests a single value into the indicator.
    """

    @multidispatch
    def _ingest(
        self,
        close: RealNumber,
        timestamp: DateOrDatetime | None = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Ingests a single value into the indicator.

        Args:
            close (RealNumber): The value to ingest.
            timestamp (DateOrDatetime | None): The timestamp of the value.
                Defaults to None.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if self.is_same_period(timestamp):
            self.update(close)
        else:
            self.add(close)

        if timestamp:
            self.previous_time = timestamp

        self.clean_cache()

    @_ingest.register
    def _(
        self,
        close: Iterable[RealNumber],
        *args,
        **kwargs,
    ):
        """
        Ingests an iterable of values into the indicator.

        Args:
            close (Iterable[RealNumber]): The values to ingest.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        self.add(close)

    @_ingest.register
    def _(
        self,
        close: Iterable[RealNumber],
        timestamp: Iterable[DateOrDatetime],
        *args,
        **kwargs,
    ):
        """
        Ingests an iterable of values with timestamps into the indicator.

        Args:
            close (Iterable[RealNumber]): The values to ingest.
            timestamp (Iterable[DateOrDatetime]): The timestamps of the values.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        for c, d in zip(close, timestamp):
            self._ingest(c, d)


class MultipleInputMixin:
    """
    Mixin for indicators that ingest multiple values at once.

    The `_ingest` method is called by the `ingest` method of the indicator,
    and is responsible for updating the indicator with the ingested values.

    The default implementation of `_ingest` takes an iterable of values and
    ingests each of them one by one into the indicator. The `clean_cache`
    method of the indicator is called at the end to purge the oldest values
    from the cache.

    The default implementation of `_ingest` also handles the case where
    the values are passed as separate arguments instead of an iterable.
    """

    @multidispatch
    def _ingest(
        self,
        open: Iterable[RealNumber] | None,
        high: Iterable[RealNumber] | None,
        low: Iterable[RealNumber] | None,
        close: Iterable[RealNumber] | None,
        volume: Iterable[RealNumber] | None = None,
        timestamp: Iterable[DateOrDatetime] | None = None,
    ) -> None:
        """
        Ingests a single value into the indicator.

        Args:
            open (Iterable[RealNumber] | None): The open prices.
            high (Iterable[RealNumber] | None): The high prices.
            low (Iterable[RealNumber] | None): The low prices.
            close (Iterable[RealNumber] | None): The close prices.
            volume (Iterable[RealNumber] | None): The volumes.
                Defaults to None.
            timestamp (Iterable[DateOrDatetime] | None): The timestamps.
                Defaults to None.

        Returns:
            None
        """
        # OHLCV use talipp's input sampling
        ohlcv = self.make_ohlcv(
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume,
            timestamp=timestamp,
        )
        for value in ohlcv:
            self.add(value)
        self.clean_cache()

    @_ingest.register
    def _(
        self,
        open: RealNumber | None,
        high: RealNumber | None,
        low: RealNumber | None,
        close: RealNumber | None,
        volume: RealNumber | None = None,
        timestamp: DateOrDatetime | None = None,
    ) -> None:
        """
        Ingests a single value into the indicator.

        Args:
            open (RealNumber | None): The open price.
            high (RealNumber | None): The high price.
            low (RealNumber | None): The low price.
            close (RealNumber | None): The close price.
            volume (RealNumber | None): The volume.
                Defaults to None.
            timestamp (DateOrDatetime | None): The timestamp.
                Defaults to None.

        Returns:
            None
        """
        return self._ingest(
            [open] if open is not None else None,
            [high] if high is not None else None,
            [low] if low is not None else None,
            [close] if close is not None else None,
            [volume] if volume is not None else None,
            [timestamp] if timestamp is not None else None,
        )
