import enum
from typing import Generator, Iterable

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


class SignalDirection(enum.Enum):
    UP = 1
    DOWN = -1
    FLAT = 0


@dataclass(config=ConfigDict(frozen=True, extra="forbid"))
class Signal:
    symbol: str
    direction: SignalDirection


@dataclass(config=ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True))
class SignalCollection:
    signals: list[Signal] = Field(default_factory=list)

    def __iter__(self) -> Generator[Signal, None, None]:
        return (x for x in self.signals)

    def __len__(self) -> int:
        return len(self.signals)

    def add(self, signals: Signal | Iterable[Signal]) -> None:
        if isinstance(signals, Iterable):
            self.signals.extend(signals)
        else:
            self.signals.append(signals)

    def clear(self) -> None:
        self.signals.clear()
