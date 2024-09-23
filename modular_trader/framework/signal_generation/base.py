from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from modular_trader.context import Context
    from modular_trader.signal import Signal
    from modular_trader.universe import AssetUniverse


class BaseSignalGeneration(ABC):
    """Abstract base class for signal generation.

    Attributes:
        context: Context
            The framework context.
        universe: AssetUniverse
            The asset universe to generate signals for.

    Methods:
        run(context: Context, universe: AssetUniverse) -> Iterable[Signal]:
            Must be implemented by subclasses.
            Called by __call__() to generate signals.
    """

    def __call__(self, context: Context, universe: AssetUniverse):
        """Generate signals.

        Args:
            context: Context
                The framework context.
            universe: AssetUniverse
                The asset universe to generate signals for.

        Returns:
            Iterable[Signal]:
                An iterable of signals.
        """
        signals: Iterable[Signal] = self.run(context, universe) or []
        context.signals.clear()  # clearing old before adding new
        context.signals.add(signals)

    @abstractmethod
    def run(self, context: Context, universe: AssetUniverse) -> Iterable[Signal]:
        """Must be implemented by subclasses.

        Called by __call__() to generate signals.
        """
