from typing import Iterable, Iterator
from pydantic.dataclasses import dataclass, Field, ConfigDict
from multimethod import multimethod


@dataclass(config=ConfigDict(extra="forbid"))
class AssetUniverse:
    universe: set[str] = Field(default_factory=set)
    added: set[str] = Field(default_factory=set)
    removed: set[str] = Field(default_factory=set)

    def __iter__(self) -> Iterator[str]:
        return iter(self.universe)

    @multimethod
    def add(self, symbol: str) -> None:
        if symbol not in self.universe:
            print(f"Add: {symbol=} is new.")
            self.universe.add(symbol)
            self.added.add(symbol)
            self.removed.discard(symbol)

    @add.register
    def _(self, symbols: Iterable[str]) -> None:
        for symbol in symbols:
            self.add(symbol)

    @multimethod
    def remove(self, symbol: str) -> None:
        if symbol in self.universe:
            print(f"Remove: {symbol=} exists")
            self.universe.remove(symbol)
            self.removed.add(symbol)
            self.added.discard(symbol)

    @remove.register
    def _(self, symbols: Iterable[str]) -> None:
        for symbol in symbols:
            self.remove(symbol)

    def update(self, symbols: Iterable[str]) -> None:
        to_add = set(symbols).difference(self.universe)
        to_remove = self.universe.difference(set(symbols))
        self.added.clear()
        self.removed.clear()
        self.add(to_add)
        self.remove(to_remove)
