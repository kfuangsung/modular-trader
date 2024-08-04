from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Any


class BaseEngine(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the engine"""

    @abstractmethod
    def get_logger(self): ...

    @abstractmethod
    def get_historical_data(self):
        """Get the historical data"""

    @abstractmethod
    def get_positions(self):
        """Get all positions held by the account"""

    @abstractmethod
    def get_cash(self) -> int | float:
        """Get remaining cash in the account"""

    @abstractmethod
    def get_equity(self) -> int | float:
        """Get the current equity in the account"""

    def get_orders(self) -> Any:
        """Get all active orders."""

    @abstractmethod
    def order_share(self, symbol: str, share: int | float) -> Any:
        """Place an order for a fixed number of shares."""

    @abstractmethod
    def order_value(self, symbol: str, value: int | float) -> Any:
        """Place an order for a fixed amount of money."""

    @abstractmethod
    def order_percent(self, symbol: str, percent: int | float) -> Any:
        """
        Place an order in the specified asset corresponding to the given percent of the current portfolio value.
        percent is in decimal format; 0.5 = 50%
        """

    @abstractmethod
    def order_target_share(self, symbol: str, target_share: int | float) -> Any:
        """Place an order to adjust a position to a target number of shares."""

    @abstractmethod
    def order_target_value(self, symbol: str, target_value: int | float) -> Any:
        """Place an order to adjust a position to a target amount of money."""

    @abstractmethod
    def order_target_percent(self, symbol: str, target_percent: int | float) -> Any:
        """Place an order to adjust a position to a target percent of the current portfolio value."""

    @abstractmethod
    def cancel_all_orders(self) -> Any:
        """Cancel all active orders."""

    @abstractmethod
    def cancel_orders(self, symbol: str) -> Any:
        """Cancel all active orders for a given symbol."""

    @abstractmethod
    def close_all_positions(self) -> Any:
        """Close all positions"""

    @abstractmethod
    def close_position(self, symbol: str) -> Any:
        """Close a position for a given symbol."""

    @abstractmethod
    def streaming(self) -> None:
        """Streaming data from the engine"""
