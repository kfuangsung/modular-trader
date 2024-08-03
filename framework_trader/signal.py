import enum
from typing import Iterable

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from pydantic import Field


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

    def __iter__(self):
        return (x for x in self.signals)

    def add(self, signals: Signal | Iterable[Signal]) -> None:
        if isinstance(signals, Iterable):
            self.signals.extend(signals)
        else:
            self.signals.append(signals)

    def clear(self) -> None:
        self.signals.clear()
