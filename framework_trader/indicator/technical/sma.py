from talipp.indicators import SMA as BaseSMA
from talipp.input import SamplingPeriodType

from .base import BaseIndicator, SingleInputMixin


class SMA(BaseIndicator, BaseSMA, SingleInputMixin):
    """
    Simple Moving Average (SMA)

    The Simple Moving Average (SMA) is a technical indicator that calculates the
    average of a security's price over a specified number of periods. It is used
    to identify trends and patterns in the price movement of a security. The
    indicator is a moving average of the price over a specified number of
    periods.

    Args:
        period (int): The number of periods to calculate the average over.
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

        BaseSMA.__init__(self, period, input_indicator=input_indicator)
        BaseIndicator.__init__(self, cache_size, sampling_period, input_indicator, name)
