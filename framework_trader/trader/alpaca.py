import asyncio
import math
from typing import TYPE_CHECKING

import pendulum
from alpaca.common.exceptions import APIError
from alpaca.data.enums import Adjustment
from alpaca.data.timeframe import TimeFrameUnit
from alpaca.trading.enums import AssetClass
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from framework_trader.context import Context
from framework_trader.engine.alpaca import AlpacaEngine
from framework_trader.framework.collection import FrameworkCollection
from framework_trader.indicator.handler.alpaca import AlpacaIndicatorHandler, Frequency
from framework_trader.record import Recorder
# from framework_trader.universe import AssetUniverse

from .base import BaseTrader

if TYPE_CHECKING:
    import pandas as pd


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True))
class AlpacaTrader(BaseTrader):
    engine: AlpacaEngine
    framework: FrameworkCollection
    subscription_symbols: list[str]
    indicator: AlpacaIndicatorHandler | None = Field(default=None)
    context: Context = Field(default_factory=Context)
    recorder: Recorder = Field(default_factory=Recorder)

    def run(self):
        self.init_subscription()
        asyncio.run(self.engine.streaming())

    def init_subscription(self):
        self.engine.subscribe_trade_update(self.handle_trade_update)
        self.engine.subscribe_minute_bars(
            self.handle_minute_bars, self.subscription_symbols
        )
        self.engine.subscribe_daily_bars(
            self.handle_daily_bars, self.subscription_symbols
        )

    # def manage_subscription(self, universe: AssetUniverse):
    #     # sub/unsubscribe during runtime ?
    #     if len(universe.added) > 0:
    #         self.engine.subscribe_minute_bars(self.handle_minute_bars, universe.added)
    #         self.engine.subscribe_daily_bars(self.handle_daily_bars, universe.added)

    #     if len(universe.removed) > 0:
    #         self.engine.unsubscribe_minute_bars(*universe.removed)
    #         self.engine.unsubscribe_daily_bars(*universe.removed)

    async def handle_trade_update(self, data):
        self.logger.info(
            f"{data.event} {data.order.side}`{data.order.symbol}` @{data.price} x {data.qty} | position_qty: {data.position_qty}"
        )

        # record
        self.recorder["positions"] = self.engine.get_positions()
        self.recorder["indicators"] = self.indicator.attached_indicators
        self.recorder.save_to_disk()

    async def handle_minute_bars(self, bar):
        if self.indicator.frequency == Frequency.MINUTE:
            self.indicator.update(bar)

    async def handle_daily_bars(self, bar):
        self.framework.asset_selection(self.context)
        # self.manage_subscription(self.context.universe)
        self.indicator.init_indicator(self.context.universe)
        if not self.indicator.is_warmup:
            self.logger.debug("Warming up indicator")
            data: pd.DataFrame = self.get_historical_data(
                self.indicator.symbols,
                self.indicator.warmup_length,
                self.indicator.frequency,
            )
            self.indicator.warmup(data)

        if self.indicator.frequency == Frequency.DAY:
            self.indicator.update(bar)

        self.framework.signal_generation(self.context, self.context.universe)
        self.framework.portfolio_builder(self.context, self.context.signals)
        self.framework.risk_management(self.context, self.context.allocations)
        self.framework.order_execution(self.context, self.context.allocations)

    def get_n_trading_days_in_year(self, asset_class: AssetClass) -> int | float:
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
        end: pendulum.DateTime = pendulum.now()
        if delay:
            end = end.subtract(minutes=15)

        match Frequency:
            case Frequency.MINUTE:
                n_min_per_day: int = self.get_n_trading_minutes_in_day(
                    self.engine.asset_class
                )
                n_days: int = math.ceil(length / n_min_per_day)
                start: pendulum.DateTime = end.subtract(days=n_days)
                timeframe: TimeFrameUnit = TimeFrameUnit.Minute
            case Frequency.DAY:
                n_day_per_year: int = self.get_n_trading_days_in_year(
                    self.engine.asset_class
                )
                n_years: int = math.ceil(length / n_day_per_year)
                start = end.subtract(years=n_years)
                timeframe: TimeFrameUnit = TimeFrameUnit.Day
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

        return data.df
