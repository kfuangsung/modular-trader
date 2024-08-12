# from __future__ import annotations

from pydantic import ConfigDict, BaseModel
# from pydantic.dataclasses import dataclass

from framework_trader.framework.asset_selection.base import BaseAssetSelection
from framework_trader.framework.order_execution.base import BaseOrderExecution
from framework_trader.framework.portfolio_builder.base import BasePortfolioBuilder
from framework_trader.framework.risk_management.base import BaseRiskManagement
from framework_trader.framework.signal_generation.base import BaseSignalGeneration

# from typing import TYPE_CHECKING


# if TYPE_CHECKING:
#     from framework_trader.context import Context


# @dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))


class FrameworkCollection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)
    asset_selection: BaseAssetSelection
    signal_generation: BaseSignalGeneration
    portfolio_builder: BasePortfolioBuilder
    order_execution: BaseOrderExecution
    risk_management: BaseRiskManagement

    # def run(self, context: Context):
    #     self.asset_selection(context)
    #     self.signal_generation(context, context.universe)
    #     self.portfolio_builder(context, context.signals)
    #     self.risk_management(context, context.allocations)
    #     self.order_execution(context, context.allocations)

    # symbols: Iterable[str] = self.asset_selection.run(self.context)
    # self.universe.update(symbols)

    # signals: Iterable[Signal] = self.signal_generation.run(
    #     self.context, self.universe
    # )
    # self.context.signals.add(signals)

    # # create portfolio allocations
    # allocations: Iterable[Allocation] = self.portfolio_builder.run(
    #     self.context, signals
    # )
    # # option to modify allocations
    # allocations: Iterable[Allocation] = self.risk_management.run(
    #     self.context, allocations
    # )
    # self.context.allocations.add(allocations)

    # # submit orders
    # self.order_execution.run(self.context, self.context.allocations)
    # self.context.signals.clear()
    # self.context.allocations.clear()
