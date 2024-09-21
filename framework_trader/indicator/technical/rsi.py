from talipp.indicators import RSI as BaseRSI
from talipp.input import SamplingPeriodType

from .base import BaseIndicator, SingleInputMixin


class RSI(BaseIndicator, BaseRSI, SingleInputMixin):
    """
    Relative Strength Index (RSI)

    The RSI is a technical indicator used to measure the strength of a stock or
    currency's recent price action. It is an oscillator that computes the speed and
    change of price movements by comparing the magnitude of recent gains to recent
    losses. The RSI is usually plotted below an asset's price chart and can have a
    reading from 0 to 100. Readings above 70 are considered overbought while
    readings below 30 are considered oversold.

    Args:
        period (int): The period of the RSI.
        input_indicator (BaseIndicator | None): The input indicator.
        sampling_period (SamplingPeriodType | None): The sampling period.
        cache_size (int | None): The cache size.
        name (str | None): The name of the indicator.
    """
    def __init__(
        self,
        period: int,
        input_indicator: BaseIndicator | None = None,
        sampling_period: SamplingPeriodType | None = None,
        cache_size: int | None = None,
        name: str | None = None,
    ):
        cache_size = cache_size or period
        assert cache_size >= period, f"Cache size must be at least {self.period}"
        name = name or f"{self.__class__.__name__}_{period}"

        BaseRSI.__init__(self, period, input_indicator=input_indicator)
        BaseIndicator.__init__(self, cache_size, sampling_period, input_indicator, name)
