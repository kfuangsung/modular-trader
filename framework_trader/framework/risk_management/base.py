from abc import ABC, abstractmethod
from framework_trader.allocation import AllocationCollection
from framework_trader.context import Context


class BaseRiskManagement(ABC):
    def __call__(self, context: Context, allocations: AllocationCollection):
        allocations = self.run(context, allocations)

    @abstractmethod
    def run(
        self, context: Context, allocations: AllocationCollection
    ) -> AllocationCollection: ...
