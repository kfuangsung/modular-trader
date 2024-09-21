from __future__ import annotations

import asyncio
import math
from typing import TYPE_CHECKING

import pendulum
from alpaca.common.exceptions import APIError
from alpaca.data.enums import Adjustment
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import AssetClass

from framework_trader.context import Context
from framework_trader.engine.alpaca import AlpacaEngine
from framework_trader.framework.collection import FrameworkCollection
from framework_trader.indicator.handler.alpaca import AlpacaIndicatorHandler, Frequency
from framework_trader.record import Recorder

from .base import BaseTrader

if TYPE_CHECKING:
    import pandas as pd


class AlpacaTrader(BaseTrader):
    """
    A trader class that uses Alpaca as the engine.

    This class is responsible for setting up the subscriptions, and handling the
    trade updates, minute bars, and daily bars.

    Attributes:
        engine (AlpacaEngine): The Alpaca engine instance.
        framework (FrameworkCollection): The framework instance.
        subscription_symbols (list[str]): The symbols to subscribe to.
        indicator (AlpacaIndicatorHandler | None): The indicator handler instance.
        context (Context | None): The context instance.
        recorder (Recorder | None): The recorder instance.
        is_log_heartbeat (bool): Whether to log heartbeats.
        daily_bar_heartbeat_timestamp (pendulum.DateTime): The timestamp of the
            daily bar heartbeat.
        minute_bar_heartbeat_timestamp (pendulum.DateTime): The timestamp of the
            minute bar heartbeat.
    """

    def __init__(
        self,
        engine: AlpacaEngine,
        framework: FrameworkCollection,
        subscription_symbols: list[str],
        indicator: AlpacaIndicatorHandler | None = None,
        context: Context | None = Context(),
        recorder: Recorder | None = Recorder(),
        is_log_heartbeat: bool = True,
    ):
        super().__init__(engine, framework, indicator, context, recorder)
        self.is_log_heartbeat = is_log_heartbeat
        self.subscription_symbols = subscription_symbols
        self.daily_bar_heartbeat_timestamp = pendulum.now().set(
            minute=0, second=0, microsecond=0
        )
        self.minute_bar_heartbeat_timestamp = pendulum.now().set(
            minute=0, second=0, microsecond=0
        )

    def run(self) -> None:
        """
        Run the trader.

        This method will start the engine and set up the subscriptions.
        """
        self.logger.debug("Starting")
        self.init_subscription()
        asyncio.run(self.engine.streaming())

    def init_subscription(self) -> None:
        """
        Initialize the subscriptions.

        This method will set up the subscriptions for the symbols in the
        `subscription_symbols` attribute.
        """
        self.logger.debug("Setting up subscriptions")
        self.engine.subscribe_trade_update(self.handle_trade_update)
        self.engine.subscribe_minute_bars(
            self.handle_minute_bars, self.subscription_symbols
        )
        self.engine.subscribe_daily_bars(
            self.handle_daily_bars, self.subscription_symbols
        )
        self.logger.debug("Finised setting up subscriptions")

    # def manage_subscription(self, universe: AssetUniverse):
    #     # sub/unsubscribe during runtime ?
    #     if len(universe.added) > 0:
    #         self.engine.subscribe_minute_bars(self.handle_minute_bars, universe.added)
    #         self.engine.subscribe_daily_bars(self.handle_daily_bars, universe.added)

    #     if len(universe.removed) > 0:
    #         self.engine.unsubscribe_minute_bars(*universe.removed)
    #         self.engine.unsubscribe_daily_bars(*universe.removed)

    def record_status(self) -> None:
        """
        Record the status of the trader.

        This method will record the positions, indicators, and other relevant
        information of the trader.
        """
        self.recorder["timestamp"] = pendulum.now()
        self.recorder["positions"] = self.engine.get_positions_serialize()
        if self.indicator and self.indicator.attached_indicators:
            self.recorder["indicators"] = self.indicator.attached_indicators
        self.recorder.save_to_disk()

    async def handle_trade_update(self, data) -> None:
        """
        Handle trade updates.

        This method will log the trade update and record the status of the trader.
        """
        self.logger.info(
            f"{data.event} {data.order.side}`{data.order.symbol}` @{data.price} x {data.qty} | position_qty: {data.position_qty}"
        )
        self.record_status()

    async def handle_minute_bars(self, bar) -> None:
        """
        Handle minute bars.

        This method will log the minute bar and record the status of the trader.
        """
        if pendulum.now() >= self.minute_bar_heartbeat_timestamp:
            self.logger.debug(f"{bar.symbol} | minute bars | heartbeat")
            self.minute_bar_heartbeat_timestamp = (
                self.minute_bar_heartbeat_timestamp.add(hours=1)
            )

        if self.indicator and self.indicator.frequency == Frequency.MINUTE:
            self.indicator.update(bar)
        self.record_status()

        # for sym, ind in self.indicator.attached_indicators.items():
        #     self.logger.debug(sym)
        #     for x in ind.values():
        #         self.logger.debug(x)

    async def handle_daily_bars(self, bar) -> None:
        """
        Handle daily bars.

        This method will log the daily bar and record the status of the trader.
        """
        if pendulum.now() >= self.daily_bar_heartbeat_timestamp:
            self.logger.debug(f"{bar.symbol} | daily bars | heartbeat")
            self.daily_bar_heartbeat_timestamp = self.daily_bar_heartbeat_timestamp.add(
                hours=1
            )

        self.framework.asset_selection(self.context)
        # self.manage_subscription(self.context.universe)
        if self.indicator:
            self.indicator.init_indicator(self.context.universe)
        if not self.indicator.is_warmup:
            self.logger.debug("Warming up indicator")
            data: pd.DataFrame = self.get_historical_data(
                self.indicator.symbols,
                self.indicator.warmup_length,
                self.indicator.frequency,
            )
            self.indicator.warmup(data)

        if self.indicator and self.indicator.frequency == Frequency.DAY:
            self.indicator.update(bar)

        self.framework.signal_generation(self.context, self.context.universe)
        self.framework.portfolio_builder(self.context, self.context.signals)
        self.framework.risk_management(self.context, self.context.allocations)
        self.framework.order_execution(self.context, self.context.allocations)

    def get_n_trading_days_in_year(self, asset_class: AssetClass) -> int | float:
        """
        Get the number of trading days in a year for the given asset class.

        Args:
            asset_class (AssetClass): The asset class.

        Returns:
            int | float: The number of trading days in a year.
        """
        match asset_class:
            case AssetClass.US_EQUITY:
                return 252
            case AssetClass.CRYPTO:
                return 365.25
            case AssetClass.US_OPTION:
                return 252
            case _:
                raise ValueError(f"Invalid asset class: {asset_class}")

    def get_n_trading_minutes_in_day(self, asset_class: AssetClass) -> int | float:
        """
        Get the number of trading minutes in a day for the given asset class.

        Args:
            asset_class (AssetClass): The asset class.

        Returns:
            int | float: The number of trading minutes in a day.
        """
        match asset_class:
            case AssetClass.US_EQUITY:
                return 6.5 * 60
            case AssetClass.CRYPTO:
                return 24 * 60
            case AssetClass.US_OPTION:
                return 6.5 * 60
            case _:
                raise ValueError(f"Invalid asset class: {asset_class}")

    def get_historical_data(
        self, symbols: list[str], length: int, frequency: Frequency, delay: bool = False
    ) -> pd.DataFrame:
        """
        Get the historical data.

        Args:
            symbols (list[str]): The symbols for which to get the historical data.
            length (int): The length of the historical data.
            frequency (Frequency): The frequency of the historical data.
            delay (bool): Whether to delay the request if it fails.

        Returns:
            pd.DataFrame: The historical data.
        """
        end: pendulum.DateTime = pendulum.now()
        if delay:
            end = end.subtract(minutes=15)

        match frequency:
            case Frequency.MINUTE:
                n_min_per_day: int = self.get_n_trading_minutes_in_day(
                    self.engine.asset_class
                )
                n_days: int = math.ceil(length / n_min_per_day)
                start: pendulum.DateTime = end.subtract(days=n_days)
                timeframe: TimeFrame = TimeFrame.Minute
            case Frequency.DAY:
                n_day_per_year: int = self.get_n_trading_days_in_year(
                    self.engine.asset_class
                )
                n_years: int = math.ceil(length / n_day_per_year)
                start = end.subtract(years=n_years)
                timeframe: TimeFrame = TimeFrame.Day
            case _:
                raise ValueError(f"Invalid frequency: {frequency}")

        try:
            data = self.engine.get_historical_data(
                symbols=symbols,
                start=start,
                end=end,
                timeframe=timeframe,
                adjustment=Adjustment.ALL,
            )
        except APIError as e:
            if not delay:
                self.logger.error(
                    f"{e.__class__.__name__}: {e._error} Try again with delay..."
                )
                return self.get_historical_data(symbols, length, frequency, True)
            else:
                raise e

        return data
