from talipp.indicators import Stoch as BaseSTOCH
from talipp.input import SamplingPeriodType

from .base import BaseIndicator, MultipleInputMixin


class STOCH(BaseIndicator, BaseSTOCH, MultipleInputMixin):
    """
    Stochastic Oscillator (STOCH)

    The Stochastic Oscillator is a momentum indicator that compares the closing
    price of a security to its price range over a given period of time. The
    Stochastic Oscillator is used to generate overbought and oversold signals.

    Args:
        period (int): The period of the Stochastic Oscillator.
        smoothing_period (int): The smoothing period of the Stochastic Oscillator.
        input_indicator (BaseIndicator | None): The input indicator.
        sampling_period (SamplingPeriodType | None): The sampling period.
        cache_size (int | None): The cache size.
        name (str | None): The name of the indicator.
    """

    def __init__(
        self,
        period: int,
        smoothing_period: int,
        input_indicator: BaseIndicator | None = None,
        sampling_period: SamplingPeriodType | None = None,
        cache_size: int | None = None,
        name: str | None = None,
    ):
        cache_size = cache_size or (period + smoothing_period)
        assert cache_size >= period, f"Cache size must be at least {self.period}"
        name = name or f"{self.__class__.__name__}_{period}_{smoothing_period}"

        BaseSTOCH.__init__(
            self,
            period,
            smoothing_period,
            input_indicator=input_indicator,
            input_sampling=sampling_period,
        )
        BaseIndicator.__init__(self, cache_size, sampling_period, input_indicator, name)
