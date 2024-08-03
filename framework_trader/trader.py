from __future__ import annotations
from typing import TYPE_CHECKING
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass
# from benedict import benedict

from framework_trader.context import Context
from framework_trader.engine.base import BaseEngine
from framework_trader.framework.collection import FrameworkCollection
from framework_trader.indicator.handler.base import BaseIndicatorHandler

if TYPE_CHECKING:
    from framework_trader.universe import AssetUniverse
    from framework_trader.logging.base import BaseLogger


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))
class FrameworkTrader:
    engine: BaseEngine
    framework: FrameworkCollection
    indicator: BaseIndicatorHandler | None = Field(default=None)
    context: Context = Field(default_factory=Context)

    logger: BaseLogger = property(fget=lambda self: self.engine.get_logger())
    universe: AssetUniverse = property(fget=lambda self: self.context.universe)

    def run(self):
        self.engine.stream(self.context, self.framework, self.indicator)
