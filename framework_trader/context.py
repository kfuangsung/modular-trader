from typing import Mapping
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from framework_trader.indicator.ta.base import BaseIndicator
from framework_trader.allocation import AllocationCollection
from framework_trader.signal import SignalCollection
from framework_trader.universe import AssetUniverse


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="allow"))
class Context:
    universe: AssetUniverse = Field(default_factory=AssetUniverse)
    signals: SignalCollection = Field(default_factory=SignalCollection)
    allocations: AllocationCollection = Field(default_factory=AllocationCollection)
    indicators: Mapping[str, Mapping[str, BaseIndicator]] = Field(default_factory=dict)
