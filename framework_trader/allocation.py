from typing import Generator, Iterable, TypeAlias

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(frozen=True, extra="forbid"))
class AllocationTarget:
    symbol: str
    weight: int | float


@dataclass(config=ConfigDict(frozen=True, extra="forbid"))
class AllocationAdjustment:
    """
    Adjust allocation by a given weight.
    E.g.,
    5% -> increase allocation by 5%,
    -2% -> decrease allocation by 2%
    """

    symbol: str
    weight: int | float


Allocation: TypeAlias = AllocationTarget | AllocationAdjustment


@dataclass(config=ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True))
class AllocationCollection:
    allocations: list[Allocation] = Field(default_factory=list)

    def __iter__(self) -> Generator[Allocation, None, None]:
        return (x for x in self.allocations)

    def __len__(self) -> int:
        return len(self.allocations)

    @property
    def symbols(self) -> set[str]:
        return set([x.symbol for x in self.allocations])

    def add(self, allocations: Allocation | Iterable[Allocation]) -> None:
        if isinstance(allocations, Iterable):
            self.allocations.extend(allocations)
        else:
            self.allocations.append(allocations)

    def clear(self) -> None:
        self.allocations.clear()

    def remove_symbol(self, symbol: str):
        self.allocations = [
            alloc for alloc in self.allocations if alloc.symbol != symbol
        ]
