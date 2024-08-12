from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic.dataclasses import dataclass
from typing_extensions import override

from framework_trader.allocation import (
    AllocationAdjustment,
    AllocationCollection,
    AllocationTarget,
)

from .base import BaseOrderExecution

if TYPE_CHECKING:
    from framework_trader.context import Context


@dataclass
class InstantOrderExecution(BaseOrderExecution):
    """Instantly execute orders from allocations"""

    @override
    def run(self, context: Context, allocations: AllocationCollection) -> None:
        if allocations is None or len(allocations) == 0:
            return
        symbols_in_orders = [x.symbol for x in context.engine.get_orders()]
        for allocation in allocations:
            # skip if order is pending
            if allocation.symbol in symbols_in_orders:
                continue
            if isinstance(allocation, AllocationTarget):
                if allocation.weight == 0:
                    context.engine.close_position(allocation.symbol)
                else:
                    context.engine.order_target_percent(
                        allocation.symbol, allocation.weight
                    )
            elif isinstance(allocation, AllocationAdjustment):
                if allocation.weight != 0:
                    context.engine.order_percent(allocation.symbol, allocation.weight)
            else:
                raise TypeError(f"Unknown allocation type: {type(allocation)}")
