from abc import ABC, abstractmethod
from typing import Iterable

from framework_trader.signal import Signal
from framework_trader.context import Context
from framework_trader.universe import AssetUniverse


class BaseSignalGeneration(ABC):
    def __call__(self, context: Context, universe: AssetUniverse):
        signals: Iterable[Signal] = self.run(context, universe)
        context.signals.add(signals)

    @abstractmethod
    def run(self, context: Context, universe: AssetUniverse) -> Iterable[Signal]: ...
