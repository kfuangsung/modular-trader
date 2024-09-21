from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from framework_trader.allocation import AllocationCollection
    from framework_trader.context import Context


class BaseRiskManagement(ABC):
    """
    Base class for risk management.

    This class defines the interface for all risk management strategies.

    The `__call__` method is called by the framework to apply the risk
    management strategy to the given allocations.

    The `run` method is called by `__call__` and should be implemented by
    subclasses to perform the actual risk management logic.
    """

    def __call__(self, context: Context, allocations: AllocationCollection):
        allocations = self.run(context, allocations)

    @abstractmethod
    def run(
        self, context: Context, allocations: AllocationCollection
    ) -> AllocationCollection: ...
