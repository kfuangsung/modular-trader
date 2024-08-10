from typing import Iterable

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import override

from framework_trader.context import Context
from framework_trader.signal import Signal, SignalDirection
from framework_trader.universe import AssetUniverse

from .base import BaseSignalGeneration


@dataclass
class ConstantSignalGeneration(BaseSignalGeneration):
    direction: SignalDirection = Field(default=SignalDirection.UP)

    @override
    def run(self, context: Context, universe: AssetUniverse) -> Iterable[Signal]:
        return [Signal(symbol, self.direction) for symbol in universe]
