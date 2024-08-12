from talipp.indicators import RSI as BaseRSI
from talipp.input import SamplingPeriodType

from .base import BaseIndicator, SingleInputMixin


class RSI(BaseIndicator, BaseRSI, SingleInputMixin):
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
