from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# from benedict import benedict
from framework_trader.context import Context
from framework_trader.engine.base import BaseEngine
from framework_trader.framework.collection import FrameworkCollection
from framework_trader.indicator.handler.base import BaseIndicatorHandler
from framework_trader.record import Recorder

# from pydantic import ConfigDict, Field
# from pydantic.dataclasses import dataclass


if TYPE_CHECKING:
    from framework_trader.logging.base import BaseLogger

    # from framework_trader.universe import AssetUniverse


# @dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))
class BaseTrader(ABC):
    # engine: BaseEngine
    # framework: FrameworkCollection
    # indicator: BaseIndicatorHandler | None
    # context: Context

    def __init__(
        self,
        engine: BaseEngine,
        framework: FrameworkCollection,
        indicator: BaseIndicatorHandler,
        context: Context,
        recorder: Recorder,
    ):
        self.engine = engine
        self.framework = framework
        self.indicator = indicator
        self.context = context
        self.recorder = recorder
        self.context.indicators = indicator
        self.context.engine = engine

    logger: BaseLogger = property(fget=lambda self: self.engine.get_logger())

    # def __post_init__(self):
    #     self.context.engine = self.engine

    @abstractmethod
    def run(self):
        ...
        # asyncio.run(self.engine.streaming())
