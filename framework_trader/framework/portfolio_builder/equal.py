from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from typing_extensions import override

from framework_trader.allocation import AllocationTarget
from framework_trader.signal import SignalDirection

from .base import BasePortfolioBuilder

if TYPE_CHECKING:
    from framework_trader.allocation import Allocation
    from framework_trader.context import Context
    from framework_trader.signal import SignalCollection


class EqualWeightPortfolioBuilder(BasePortfolioBuilder):
    @override
    def run(self, context: Context, signals: SignalCollection) -> Iterable[Allocation]:
        filtered_signals = [s for s in signals if s.direction == SignalDirection.UP]
        if len(filtered_signals) == 0:
            return []
        w = 1 / len(filtered_signals)

        return [AllocationTarget(s.symbol, w) for s in filtered_signals]
