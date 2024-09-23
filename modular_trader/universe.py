from typing import Iterable, Iterator

from multimethod import multimethod
from pydantic.dataclasses import ConfigDict, Field, dataclass


@dataclass(config=ConfigDict(extra="forbid"))
class AssetUniverse:
    """Manage the dynamic list of assets in the strategy universe.

    Attributes:
        universe (set[str]): The set of assets that are currently in the
            universe.
        added (set[str]): The set of assets that have been added in the current
            context.
        removed (set[str]): The set of assets that have been removed in the
            current context.
    """

    universe: set[str] = Field(default_factory=set)
    added: set[str] = Field(default_factory=set)
    removed: set[str] = Field(default_factory=set)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the assets in the universe."""
        return iter(self.universe)

    @multimethod
    def add(self, symbol: str) -> None:
        """Add a single asset to the universe.

        If the asset is not already in the universe, it is added and the added
        set is updated. If the asset is already in the universe, the added set
        is not updated.

        Args:
            symbol (str): The symbol of the asset to add.
        """
        if symbol not in self.universe:
            # print(f"Add: {symbol=} is new.")
            self.universe.add(symbol)
            self.added.add(symbol)
            self.removed.discard(symbol)

    @add.register
    def _(self, symbols: Iterable[str]) -> None:
        """Add multiple assets to the universe.

        Args:
            symbols (Iterable[str]): The symbols of the assets to add.
        """
        for symbol in symbols:
            self.add(symbol)

    @multimethod
    def remove(self, symbol: str) -> None:
        """Remove a single asset from the universe.

        If the asset is in the universe, it is removed and the removed set is
        updated. If the asset is not in the universe, the removed set is not
        updated.

        Args:
            symbol (str): The symbol of the asset to remove.
        """
        if symbol in self.universe:
            # print(f"Remove: {symbol=} exists")
            self.universe.remove(symbol)
            self.removed.add(symbol)
            self.added.discard(symbol)

    @remove.register
    def _(self, symbols: Iterable[str]) -> None:
        """Remove multiple assets from the universe.

        Args:
            symbols (Iterable[str]): The symbols of the assets to remove.
        """
        for symbol in symbols:
            self.remove(symbol)

    def update(self, symbols: Iterable[str]) -> None:
        """Update the universe by adding and removing assets.

        The added and removed sets are cleared before updating the universe.

        Args:
            symbols (Iterable[str]): The symbols of the assets to add to the
                universe.
        """
        to_add = set(symbols).difference(self.universe)
        to_remove = self.universe.difference(set(symbols))
        self.added.clear()
        self.removed.clear()
        self.add(to_add)
        self.remove(to_remove)
