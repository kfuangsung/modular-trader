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
    symbols: list[str]

    @override
    def run(self, context: Context) -> Iterable[str]:
        return self.symbols
