from typing import Mapping

from pydantic import BaseModel, ConfigDict, Field

from framework_trader.allocation import AllocationCollection
from framework_trader.engine.base import BaseEngine
from framework_trader.indicator.handler.base import BaseIndicatorHandler
from framework_trader.signal import SignalCollection
from framework_trader.universe import AssetUniverse


class Context(BaseModel):
    """
    The framework context.

    Attributes:
        universe (AssetUniverse): The asset universe.
        signals (SignalCollection): The collection of signals.
        allocations (AllocationCollection): The collection of allocations.
        indicators (BaseIndicatorHandler | None): The indicator handler, if any.
        engine (BaseEngine | None): The engine, if any.
        latest_prices (Mapping[str, float]): The latest prices of all assets.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    universe: AssetUniverse = Field(default_factory=AssetUniverse)
    signals: SignalCollection = Field(default_factory=SignalCollection)
    allocations: AllocationCollection = Field(default_factory=AllocationCollection)
    indicators: BaseIndicatorHandler | None = Field(default=None)
    engine: BaseEngine | None = Field(default=None)
    latest_prices: Mapping[str, float] = Field(default_factory=dict)

    logger = property(fget=lambda self: self.engine.get_logger())
