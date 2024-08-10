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
        orders = context.engine.get_orders()
        symbols_in_orders = [x.symbol for x in orders]
        for allocation in allocations:
            # skip if order is pending
            if allocation.symbol in symbols_in_orders:
                continue
            if isinstance(allocation, AllocationTarget):
                context.engine.order_target_percent(
                    allocation.symbol, allocation.weight
                )
            elif isinstance(allocation, AllocationAdjustment):
                context.engine.order_percent(allocation.symbol, allocation.weight)
            else:
                raise TypeError(f"Unknown allocation type: {type(allocation)}")

        # liquidate positions no longer needed
        pos: list[str] = [p.symbols for p in context.engine.get_positions()]
        alloc_symbols: set[str] = allocations.symbols
        to_liquidate = alloc_symbols.difference(pos)
        for symbol in to_liquidate:
            context.engine.close_position(symbol)
