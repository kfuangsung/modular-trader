from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

# from benedict import benedict
from framework_trader.context import Context
from framework_trader.engine.base import BaseEngine
from framework_trader.framework.collection import FrameworkCollection
from framework_trader.indicator.handler.base import BaseIndicatorHandler

if TYPE_CHECKING:
    from framework_trader.logging.base import BaseLogger
    # from framework_trader.universe import AssetUniverse


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))
class BaseTrader(ABC):
    engine: BaseEngine
    framework: FrameworkCollection
    indicator: BaseIndicatorHandler | None = Field(default=None)
    context: Context = Field(default_factory=Context)

    logger: BaseLogger = property(fget=lambda self: self.engine.get_logger())

    def __post_init__(self):
        self.context.engine = self.engine

    @abstractmethod
    def run(self):
        ...
        # asyncio.run(self.engine.streaming())
