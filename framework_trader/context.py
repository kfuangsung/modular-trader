from typing import Mapping

from pydantic import BaseModel, ConfigDict, Field

from framework_trader.allocation import AllocationCollection
from framework_trader.engine.base import BaseEngine
from framework_trader.indicator.handler.base import BaseIndicatorHandler
from framework_trader.signal import SignalCollection
from framework_trader.universe import AssetUniverse

# from pydantic.dataclasses import dataclass


# @dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="allow"))
class Context(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    universe: AssetUniverse = Field(default_factory=AssetUniverse)
    signals: SignalCollection = Field(default_factory=SignalCollection)
    allocations: AllocationCollection = Field(default_factory=AllocationCollection)
    indicators: BaseIndicatorHandler | None = Field(default=None)
    engine: BaseEngine | None = Field(default=None)
    latest_prices: Mapping[str, float] = Field(default_factory=dict)

    logger = property(fget=lambda self: self.engine.get_logger())
