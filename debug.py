from datetime import datetime
from framework_trader.indicator.technical import STOCH
import pandas as pd
from talipp.input import SamplingPeriodType

stoch = STOCH(period=10, smoothing_period=12, sampling_period=SamplingPeriodType.DAY_1)
ohlcv = stoch.make_ohlcv(
    open=range(100),
    high=range(100),
    low=range(100),
    close=range(100),
    timestamp=list(pd.date_range(end="2025-01-01", periods=100, freq="d")),
)
print(type(ohlcv))
stoch.add(ohlcv)
stoch.ingest(
    timestamp =[datetime(2033, 1, 1), datetime(2033, 1, 2)],
    open=[10, 11],
    high=[10, 12],
    low= [10, 12],
    close=[10, 12],
    volume=[1000, 20000],
)
# print(type(ohlcv), ohlcv)
# stoch.add(ohlcv)

print(stoch.output_values)
print(stoch.value)
