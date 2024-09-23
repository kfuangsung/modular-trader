from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from modular_trader.allocation import Allocation
    from modular_trader.context import Context
    from modular_trader.signal import SignalCollection


class BasePortfolioBuilder(ABC):
    """
    Base class for portfolio builders.

    This class defines the interface for all portfolio builders.

    The `__call__` method is called by the framework to build the portfolio.
    It is expected to clear the current allocations and add the new allocations.

    The `run` method is called by `__call__` to build the portfolio.
    It is expected to return an iterable of `Allocation` objects.
    """

    def __call__(self, context: Context, signals: SignalCollection) -> Any:
        allocations: Iterable[Allocation] = self.run(context, signals) or []
        context.allocations.clear()  # clearing old before adding new
        context.allocations.add(allocations)

    @abstractmethod
    def run(
        self, context: Context, signals: SignalCollection
    ) -> Iterable[Allocation]: ...
