from pydantic.dataclasses import dataclass
from pydantic import Field, ConfigDict
from framework_trader.engine.base import BaseEngine
from framework_trader.framework.collection import FrameworkCollection
from framework_trader.indicator.handler.base import BaseIndicatorHandler


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))
class FrameworkTrader:
    engine: BaseEngine
    framework: FrameworkCollection
    indicator: BaseIndicatorHandler

    logger = property(fget=lambda self: self.logger)
