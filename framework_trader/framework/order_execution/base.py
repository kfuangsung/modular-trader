from abc import ABC
from framework_trader.allocation import AllocationCollection
from framework_trader.context import Context


class BaseOrderExecution(ABC):
    def __call__(self, context: Context, allocations: AllocationCollection) -> None:
        self.run(context, allocations)
        context.signals.clear()
        context.allocations.clear()

    def run(self, context: Context, allocations: AllocationCollection) -> None: ...
