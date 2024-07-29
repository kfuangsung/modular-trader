from talipp.indicators import SMA as BaseSMA
from talipp.input import SamplingPeriodType


from .base import BaseIndicator, SingleInputMixin


class SMA(BaseIndicator, BaseSMA, SingleInputMixin):
    def __init__(
        self,
        period: int,
        input_indicator: BaseIndicator | None = None,
        sampling_period: SamplingPeriodType | None = None,
        cache_size: int | None = None,
    ):
        cache_size = cache_size or period
        assert cache_size >= period, f"Cache size must be at least {self.period}"

        BaseSMA.__init__(self, period, input_indicator=input_indicator)
        BaseIndicator.__init__(self, cache_size, sampling_period, input_indicator)
