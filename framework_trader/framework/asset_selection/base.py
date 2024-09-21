from abc import ABC, abstractmethod
from typing import Iterable

from framework_trader.context import Context


class BaseAssetSelection(ABC):
    """
    Base class for asset selection.

    This class defines the interface for all asset selection strategies.
    """

    def __call__(self, context: Context):
        """
        Selects the assets to be used in the backtest.

        Called by the framework to select the assets to be used in the backtest.
        """
        symbols: Iterable[str] = self.run(context) or []
        context.universe.update(symbols)

    @abstractmethod
    def run(self, context: Context) -> Iterable[str]:
        """
        Selects the assets to be used in the backtest.

        Must be implemented by subclasses.
        """
        ...
