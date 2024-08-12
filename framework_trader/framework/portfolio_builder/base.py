from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from framework_trader.allocation import Allocation
    from framework_trader.context import Context
    from framework_trader.signal import SignalCollection


class BasePortfolioBuilder(ABC):
    def __call__(self, context: Context, signals: SignalCollection) -> Any:
        allocations: Iterable[Allocation] = self.run(context, signals) or []
        context.allocations.clear()  # clearing old before adding new
        context.allocations.add(allocations)

    @abstractmethod
    def run(
        self, context: Context, signals: SignalCollection
    ) -> Iterable[Allocation]: ...
