from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from modular_trader.context import Context
from modular_trader.engine.base import BaseEngine
from modular_trader.framework.collection import FrameworkCollection
from modular_trader.indicator.handler.base import BaseIndicatorHandler
from modular_trader.record import Recorder

if TYPE_CHECKING:
    from modular_trader.logging.base import BaseLogger


class BaseTrader(ABC):
    """
    Abstract base class for traders.

    Attributes:
        engine (BaseEngine): The engine to use for running the backtest.
        framework (FrameworkCollection): The framework to use for running the backtest.
        indicator (BaseIndicatorHandler | None): The indicator to use for running the backtest.
        context (Context): The context to use for running the backtest.
        recorder (Recorder): The recorder to use for running the backtest.

    Properties:
        logger (BaseLogger): The logger to use for logging.

    Methods:
        run ():
            Runs the backtest.
    """

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

    @abstractmethod
    def run(self):
        ...
        # asyncio.run(self.engine.streaming())
