from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from .base import BaseRiskManagement

if TYPE_CHECKING:
    from framework_trader.allocation import AllocationCollection
    from framework_trader.context import Context


class NullRiskManagement(BaseRiskManagement):
    """No-op risk management strategy.

    Leaves allocations unchanged.
    """
    @override
    def run(
        self, context: Context, allocations: AllocationCollection
    ) -> AllocationCollection:
        return allocations
