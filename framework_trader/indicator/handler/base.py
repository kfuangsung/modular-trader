from abc import ABC, abstractmethod


class BaseIndicatorHandler(ABC):
    @abstractmethod
    def initialize(self):
        return NotImplemented

    @abstractmethod
    def warmup(self):
        return NotImplemented

    @abstractmethod
    def on_update(self):
        return NotImplemented
