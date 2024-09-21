from __future__ import annotations

# from copy import deepcopy
from typing import TYPE_CHECKING, Iterable

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .base import BaseAssetSelection

if TYPE_CHECKING:
    from framework_trader.context import Context


@dataclass
class ManualAssetSelection(BaseAssetSelection):
    """
    Selects the assets based on a predefined list of symbols.

    This class is used when the assets to be traded are known in advance.

    Attributes:
        symbols (list[str]): A list of symbol strings.
    """

    symbols: list[str]

    @override
    def run(self, context: Context) -> Iterable[str]:
        """
        Selects the assets based on a predefined list of symbols.

        Args:
            context (Context): The framework context.

        Returns:
            Iterable[str]: An iterable of symbol strings.
        """
        return self.symbols
