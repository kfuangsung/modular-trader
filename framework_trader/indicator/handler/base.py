from abc import ABC, abstractmethod


class BaseIndicatorHandler(ABC):
    """Abstract base class for indicator handlers."""

    @abstractmethod
    def warmup(self):
        """Warmup the indicators.

        This method is called once when the indicator handler is created.
        """
        return NotImplemented

    @abstractmethod
    def update(self):
        """Update the indicators.

        This method is called for each new bar.
        """
        return NotImplemented
