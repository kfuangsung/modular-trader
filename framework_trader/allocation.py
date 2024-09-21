from typing import Generator, Iterable, TypeAlias

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(frozen=True, extra="forbid"))
class AllocationTarget:
    """
    A target allocation of a single asset.

    Attributes:
        symbol: The symbol of the asset.
        weight: The target weight of the asset in the portfolio.
    """

    symbol: str
    weight: int | float


@dataclass(config=ConfigDict(frozen=True, extra="forbid"))
class AllocationAdjustment:
    """
    Adjust allocation by a given weight.

    For example, 5% will increase allocation by 5%, while -2% will decrease
    allocation by 2%

    Attributes:
        symbol: The symbol of the asset.
        weight: The amount to increase or decrease the allocation by.
    """

    symbol: str
    weight: int | float


Allocation: TypeAlias = AllocationTarget | AllocationAdjustment


@dataclass(config=ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True))
class AllocationCollection:
    """
    A collection of allocations.

    Attributes:
        allocations: The list of allocations.
    """

    allocations: list[Allocation] = Field(default_factory=list)

    def __iter__(self) -> Generator[Allocation, None, None]:
        """Iterate over all allocations."""
        return (x for x in self.allocations)

    def __len__(self) -> int:
        """Return the number of allocations."""
        return len(self.allocations)

    @property
    def symbols(self) -> set[str]:
        """Return all symbols in the collection."""
        return set([x.symbol for x in self.allocations])

    def add(self, allocations: Allocation | Iterable[Allocation]) -> None:
        """
        Add one or more allocations to the collection.

        Args:
            allocations: The allocation(s) to add.
        """
        if isinstance(allocations, Iterable):
            self.allocations.extend(allocations)
        else:
            self.allocations.append(allocations)

    def clear(self) -> None:
        """Clear all allocations."""
        self.allocations.clear()

    def remove_symbol(self, symbol: str):
        """
        Remove all allocations with the given symbol.

        Args:
            symbol: The symbol to remove.
        """
        self.allocations = [
            alloc for alloc in self.allocations if alloc.symbol != symbol
        ]
