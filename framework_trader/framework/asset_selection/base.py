from abc import ABC, abstractmethod
from typing import Iterable
from framework_trader.context import Context


class BaseAssetSelection(ABC):
    def __call__(self, context: Context):
        symbols: Iterable[str] = self.run(self.context)
        context.universe.update(symbols)

    @abstractmethod
    def run(self, context: Context) -> Iterable[str]: ...
