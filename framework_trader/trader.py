from pydantic.dataclasses import dataclass
from pydantic import Field, ConfigDict
from framework_trader.engine.base import BaseEngine


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))
class FrameworkTrader:
    engine: BaseEngine

    logger = property(fget=lambda self: self.logger)
