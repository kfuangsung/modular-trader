from datetime import datetime, timedelta
from talipp.input import SamplingPeriodType
from framework_trader.indicator.ta import STOCH

stoch = STOCH(period=12, smoothing_period=4, sampling_period=SamplingPeriodType.DAY_1)

print(stoch.cache_size)

day = datetime(2024, 1, 1)
for x in range(100):
    stoch.ingest(x, x + 2, x - 2, x + 1, day)
    day += timedelta(days=1)

print(stoch.input_values)
print(stoch.output_values)
print(stoch.is_ready, stoch.value)
print(len(stoch))
