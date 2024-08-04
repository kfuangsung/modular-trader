from framework_trader.allocation import (
    AllocationCollection,
    AllocationTarget,
    AllocationAdjustment,
)
from framework_trader.context import Context
from .base import BaseOrderExecution
from typing_extensions import override


class InstantOrderExecution(BaseOrderExecution):
    @override
    def run(self, context: Context, allocations: AllocationCollection) -> None:
        for allocation in allocations:
            if isinstance(allocation, AllocationTarget):
                context.engine.order_target_percent(
                    allocation.symbol, allocation.weight
                )
            elif isinstance(allocation, AllocationAdjustment):
                context.engine.order_percent(allocation.symbol, allocation.weight)
            else:
                raise TypeError(f"Unknown allocation type: {type(allocation)}")
