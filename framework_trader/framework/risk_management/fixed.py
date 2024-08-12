from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import override

from framework_trader.allocation import AllocationTarget

from .base import BaseRiskManagement

if TYPE_CHECKING:
    from framework_trader.allocation import AllocationCollection
    from framework_trader.context import Context


@dataclass
class FixedStopLossRiskManagement(BaseRiskManagement):
    """
    Fixed stop loss
    Liquidate positions if unrealized loss percent >= percent_loss
    """

    percent_loss: float = Field(default=0.10)

    @override
    def run(
        self, context: Context, allocations: AllocationCollection
    ) -> AllocationCollection:
        # get PnL percent for each positions
        unreal_pnl_pcts = {
            p.symbol: float(p.unrealized_plpc) for p in context.engine.get_positions()
        }
        for symbol, pct_loss in unreal_pnl_pcts.items():
            # liquidate if loss greather than percent_loss
            if pct_loss <= -self.percent_loss:
                allocations.remove_symbol(symbol)
                allocations.add(AllocationTarget(symbol, 0))
