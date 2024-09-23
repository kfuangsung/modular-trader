from abc import ABC, abstractmethod

from modular_trader.allocation import AllocationCollection
from modular_trader.context import Context


class BaseOrderExecution(ABC):
    """
    Base class for order execution strategies.

    Note that run() is called by __call__() and should not be called directly.
    """
    def __call__(self, context: Context, allocations: AllocationCollection) -> None:
        self.run(context, allocations)
        # context.signals.clear()
        # context.allocations.clear()

    @abstractmethod
    def run(self, context: Context, allocations: AllocationCollection) -> None: 
        """
        Execute orders from the given allocations.

        This method is called by __call__() and should not be called directly.
        """
    ...
