from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .base import BaseSignalGeneration

if TYPE_CHECKING:
    from framework_trader.context import Context
    from framework_trader.universe import AssetUniverse


@dataclass
class NullSignalGeneration(BaseSignalGeneration):
    """Signal generation strategy that doesn't generate any signals.

    This signal generation strategy is useful for testing or debugging purposes.
    """

    @override
    def run(self, context: Context, universe: AssetUniverse) -> Iterable[None]:
        """Returns an empty iterable of signals."""
        return []
