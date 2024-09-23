import enum
from typing import Generator, Iterable

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


class SignalDirection(enum.Enum):
    """
    The direction of a signal.

    This enum defines the possible directions of a signal.
    The direction can be one of the following values:
    - `UP`: The signal is indicating a long position.
    - `DOWN`: The signal is indicating a short position.
    - `FLAT`: The signal is indicating no position.
    """

    UP = 1
    DOWN = -1
    FLAT = 0


@dataclass(config=ConfigDict(frozen=True, extra="forbid"))
class Signal:
    """A signal.

    A signal is an object that contains information about a trading signal.
    The signal is defined by the following attributes:
    - `symbol`: The symbol of the asset.
    - `direction`: The direction of the signal.
    """

    symbol: str
    direction: SignalDirection


@dataclass(config=ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True))
class SignalCollection:
    """
    A collection of signals.

    This class represents a collection of trading signals.
    It contains the following attributes:
    - `signals`: A list of Signal objects.
    """

    signals: list[Signal] = Field(default_factory=list)

    def __iter__(self) -> Generator[Signal, None, None]:
        """Iterate over the signals."""
        return (x for x in self.signals)

    def __len__(self) -> int:
        """Return the number of signals."""
        return len(self.signals)

    def add(self, signals: Signal | Iterable[Signal]) -> None:
        """
        Add a signal or signals to the collection.

        Args:
            signals: A signal or an iterable of signals.
        """
        if isinstance(signals, Iterable):
            self.signals.extend(signals)
        else:
            self.signals.append(signals)

    def clear(self) -> None:
        """Clear the collection of signals."""
        self.signals.clear()
