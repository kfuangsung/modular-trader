from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import override

from framework_trader.signal import Signal, SignalDirection

from .base import BaseSignalGeneration

if TYPE_CHECKING:
    from framework_trader.context import Context
    from framework_trader.universe import AssetUniverse


@dataclass
class ConstantSignalGeneration(BaseSignalGeneration):
    """Constant signal generator.

    Generates a signal for each symbol in the universe with a constant direction.
    """
    direction: SignalDirection = Field(default=SignalDirection.UP)

    @override
    def run(self, context: Context, universe: AssetUniverse) -> Iterable[Signal]:
        """Returns an iterable of constant signals.

        Args:
            context: Context
            universe: AssetUniverse

        Returns:
            An iterable of signals.
        """
        return [Signal(symbol, self.direction) for symbol in universe]
