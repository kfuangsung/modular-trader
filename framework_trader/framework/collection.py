from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from framework_trader.framework.asset_selection.base import BaseAssetSelection
from framework_trader.framework.order_execution.base import BaseOrderExecution
from framework_trader.framework.portfolio_builder.base import BasePortfolioBuilder
from framework_trader.framework.risk_management.base import BaseRiskManagement
from framework_trader.framework.signal_generation.base import BaseSignalGeneration


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))
class FrameworkCollection:
    asset_selection: BaseAssetSelection
    signal_generation: BaseSignalGeneration
    portfolio_builder: BasePortfolioBuilder
    order_execution: BaseOrderExecution
    risk_management: BaseRiskManagement
