from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .instant import InstantOrderExecution

if TYPE_CHECKING:
    from framework_trader.allocation import AllocationCollection
    from framework_trader.context import Context


@dataclass
class ThresholdDeviationOrderExecution(InstantOrderExecution):
    """Execute orders when any current positions deviate from the allocation targets by certain threshold in percentage.

    The threshold is in decimal format; e.g. 0.05 = 5%

    Args:
        threshold (float, optional): The threshold in decimal format. Defaults to 0.05.
    """

    threshold: float = Field(default=0.05)

    @override
    def run(self, context: Context, allocations: AllocationCollection) -> None:
        if allocations is None or len(allocations) == 0:
            return
        positions = context.engine.get_positions()
        equity = context.engine.get_equity()
        # Mapping[symbol, currentWeight]
        current_weights: dict[str, float] = {
            p.symbol: float(p.market_value) / equity for p in positions
        }

        for alloc in allocations:
            if (
                abs(alloc.weight - current_weights.get(alloc.symbol, 0))
                >= self.threshold
            ):
                return super().run(context, allocations)
