from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from alpaca.common.exceptions import APIError
from alpaca.data.enums import Adjustment, CryptoFeed, DataFeed, OptionsFeed
from alpaca.data.historical import (
    CryptoHistoricalDataClient,
    OptionHistoricalDataClient,
    StockHistoricalDataClient,
)
from alpaca.data.live import CryptoDataStream, OptionDataStream, StockDataStream
from alpaca.data.models import Bar
from alpaca.data.requests import (
    CryptoBarsRequest,
    CryptoLatestBarRequest,
    OptionBarsRequest,
    StockBarsRequest,
    StockLatestBarRequest,
)
from alpaca.data.timeframe import TimeFrame
from alpaca.trading import TradingClient, TradingStream
from alpaca.trading.enums import (
    AssetClass,
    AssetStatus,
    OrderSide,
    OrderType,
    TimeInForce,
)
from alpaca.trading.models import (
    Asset,
    ClosePositionResponse,
    Order,
    Position,
    TradeAccount,
)
from alpaca.trading.requests import CancelOrderResponse, GetAssetsRequest, OrderRequest
from pydantic import ConfigDict, Field, PrivateAttr, field_validator, model_validator
from pydantic.dataclasses import dataclass
from typing_extensions import override

from framework_trader.common.enums import TradingMode
from framework_trader.logging import BaseLogger, TradingLogger

from .base import BaseEngine

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    import pandas as pd


def get_api_key() -> str | None:
    return os.environ.get("ALPACA_API_KEY", None)


def get_secret_key() -> str | None:
    return os.environ.get("ALPACA_SECRET_KEY", None)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class AlpacaEngine(BaseEngine):
    api_key: str = Field(default_factory=get_api_key)
    secret_key: str = Field(default_factory=get_secret_key)
    mode: TradingMode = Field(default=TradingMode.PAPER)
    asset_class: AssetClass = Field(default=AssetClass.US_EQUITY)
    feed: DataFeed | CryptoFeed | OptionsFeed | None = Field(default=None)
    logger: BaseLogger = Field(default_factory=TradingLogger)
    _trading_client: TradingClient = PrivateAttr(default=None)
    _trading_stream: TradingStream = PrivateAttr(default=None)
    _data_client: (
        StockHistoricalDataClient
        | CryptoHistoricalDataClient
        | OptionHistoricalDataClient
    ) = PrivateAttr(default=None)
    _data_stream: StockDataStream | CryptoDataStream | OptionDataStream = PrivateAttr(
        default=None
    )

    is_paper: bool = property(fget=lambda self: self.mode == TradingMode.PAPER)

    @field_validator("api_key")
    @classmethod
    def _api_key(cls, v: str | None) -> str:
        """validate api key"""
        if v is None:
            raise ValueError("API key not found")
        return v

    @field_validator("secret_key")
    @classmethod
    def _secret_key(cls, v: str | None) -> str:
        """validate secret key"""
        if v is None:
            raise ValueError("SECRET key not found")
        return v

    @model_validator(mode="after")
    def _initialize(self):
        """Initialize trading and data clients and streams"""
        self._init_trading()
        self._init_data()
        self._init_assets()

    def _init_trading(self):
        """Initialize trading client and stream"""
        self._trading_client = TradingClient(
            api_key=self.api_key, secret_key=self.secret_key, paper=self.is_paper
        )
        self._trading_stream = TradingStream(
            api_key=self.api_key, secret_key=self.secret_key, paper=self.is_paper
        )

    def _init_assets(self) -> dict[str, Asset]:
        assets: list = self._trading_client.get_all_assets(
            filter=GetAssetsRequest(
                status=AssetStatus.ACTIVE, asset_class=self.asset_class
            )
        )
        self._assets = {x.symbol: x for x in assets}

    def _init_data(self):
        """Initialize data clients and streams"""
        match self.asset_class:
            case AssetClass.US_EQUITY:
                self._init_stock_data()
            case AssetClass.CRYPTO:
                self._init_crypto_data()
            case AssetClass.US_OPTION:
                self._init_option_data()
            case _:
                raise ValueError("Unsupported asset class")

    def _init_stock_data(self):
        self.feed = self.feed or DataFeed.IEX
        self._data_client = StockHistoricalDataClient(
            api_key=self.api_key, secret_key=self.secret_key
        )
        self._data_stream = StockDataStream(
            api_key=self.api_key, secret_key=self.secret_key, feed=self.feed
        )

    def _init_crypto_data(self):
        self.feed = self.feed or CryptoFeed.US
        self._data_client = CryptoHistoricalDataClient(
            api_key=self.api_key, secret_key=self.secret_key
        )
        self._data_stream = CryptoDataStream(
            api_key=self.api_key, secret_key=self.secret_key, feed=self.feed
        )

    def _init_option_data(self) -> None:
        """
        Initialize data clients and streams for options trading.

        Parameters:
        - None

        This function initializes the data clients and streams for options trading. It sets the data feed to 'INDICATIVE' if not provided, and then initializes the option historical data client and option data stream with the provided API key and secret key.

        Returns:
        - None
        """
        self.feed = self.feed or OptionsFeed.INDICATIVE
        self._data_client = OptionHistoricalDataClient(
            api_key=self.api_key, secret_key=self.secret_key
        )
        self._data_stream = OptionDataStream(
            api_key=self.api_key, secret_key=self.secret_key, feed=self.feed
        )

    def is_tradeable(self, symbol: str) -> bool:
        """
        Check if the specified symbol is tradable within the specified asset class.

        Parameters:
        - symbol (str): The symbol of the asset for which the tradability should be checked.

        Returns:
        - bool: True if the specified symbol is tradable, False otherwise.
        """
        asset = self._assets.get(symbol, None)
        if asset is None:
            self.logger.warning(f"Asset `{symbol}` is not found")
            return False
        else:
            if not asset.tradable:
                self.logger.warning(f"Asset `{symbol}` is not tradable")
            return asset.tradable

    def is_fractionable(self, symbol: str) -> bool:
        """
        Check if the specified symbol is fractionable within the specified asset class.

        Parameters:
        - symbol (str): The symbol of the asset for which the tradability should be checked.

        Returns:
        - bool: True if the specified symbol is fractionable, False otherwise.
        """
        asset = self._assets.get(symbol, None)
        if asset is None:
            self.logger.warning(f"Asset `{symbol}` is not found")
            return False
        else:
            return asset.fractionable

    def get_latest_bar(self, symbol: str) -> Bar:
        """
        Get the latest bar for the specified symbol within the specified asset class.

        Parameters:
        - symbol (str): The symbol of the asset for which the latest bar is requested.

        Returns:
        - Bar: A pandas DataFrame containing the latest bar data for the specified symbol.

        Raises:
        - ValueError: If the asset class is not supported.
        - NotImplementedError: If option trading is not supported for the specified asset class.
        """
        match self.asset_class:
            case AssetClass.US_EQUITY:
                request_params = StockLatestBarRequest(
                    symbol_or_symbols=symbol, feed=self.feed
                )
                return self._data_client.get_stock_latest_bar(request_params)
            case AssetClass.CRYPTO:
                request_params = CryptoLatestBarRequest(
                    symbol_or_symbols=symbol, feed=self.feed
                )
                return self._data_client.get_crypto_latest_bar(request_params)
            case AssetClass.US_OPTION:
                raise NotImplementedError("Option trading not supported yet")
            case _:
                raise ValueError("Unsupported asset class")

    @override
    def get_name(self) -> str:
        """
        Get the name of the trading engine.

        Returns:
        - str: The name of the trading engine, which is "Alpaca" for this implementation.
        """
        return "Alpaca"

    @override
    def get_logger(self):
        return self.logger

    @override
    def get_historical_data(
        self,
        symbols: str | list[str],
        start: datetime,
        end: datetime | None = None,
        timeframe: TimeFrame | None = TimeFrame.Day,
        adjustment: Adjustment | None = Adjustment.ALL,
        **kwargs,
    ) -> dict[str, pd.DataFrame]:
        """
        Get historical data for the specified symbols within the given timeframe.

        Parameters:
        - symbols (str | list[str]): The symbols of the assets for which historical data is requested.
        - start (datetime): The start date of the historical data request.
        - end (datetime | None): The end date of the historical data request. If not provided, the current date and time will be used.
        - timeframe (TimeFrame | None): The timeframe of the historical data request. If not provided, it defaults to daily (TimeFrame.Day).
        - adjustment (Adjustment | None): The adjustment type of the historical data request. If not provided, it defaults to all (Adjustment.ALL).
        - **kwargs: Additional keyword arguments for the historical data request.

        Returns:
        - dict[str, pd.DataFrame]: A dictionary containing the historical data for each symbol as a pandas DataFrame.
        """
        match self.asset_class:
            case AssetClass.US_EQUITY:
                request_params = StockBarsRequest(
                    symbol_or_symbols=symbols,
                    start=start,
                    end=end,
                    timeframe=timeframe,
                    adjustment=adjustment,
                    feed=self.feed,
                    **kwargs,
                )
                bars = self._data_client.get_stock_bars(request_params)
            case AssetClass.CRYPTO:
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=symbols,
                    start=start,
                    end=end,
                    timeframe=timeframe,
                    **kwargs,
                )
                bars = self._data_client.get_crypto_bars(request_params)
            case AssetClass.US_OPTION:
                request_params = OptionBarsRequest(
                    symbol_or_symbols=symbols,
                    start=start,
                    end=end,
                    timeframe=timeframe,
                    **kwargs,
                )
                bars = self._data_client.get_option_bars(request_params)
            case _:
                raise ValueError("Unsupported asset class")

        df = bars.df
        symbols = df.index.droplevel(1).unique()
        return {s: df.loc[s] for s in symbols}

    @override
    def get_account(self) -> TradeAccount:
        """
        Retrieve the current trading account information.

        This function retrieves the current trading account information from the Alpaca Trading API. The returned TradeAccount object contains information such as the account's ID, cash balance, and equity value.

        Parameters:
        - None

        Returns:
        - TradeAccount: A TradeAccount object containing information about the current trading account.
        """
        return self._trading_client.get_account()

    @override
    def get_cash(self) -> float:
        """
        Retrieve the current cash balance of the trading account.

        The cash balance is the total amount of cash available in the account, which can be used to place orders or close positions.

        Parameters:
        - None

        Returns:
        - float: The current cash balance of the trading account.
        """
        account = self.get_account()
        return account.cash

    @override
    def get_equity(self) -> float:
        """
        Retrieve the current equity of the trading account.

        The equity is the total value of all open positions and cash in the account.

        Parameters:
        - None

        Returns:
        - float: The current equity of the trading account.
        """
        account = self.get_account()
        return account.equity

    @override
    def get_positions(self) -> list[Position]:
        return self._trading_client.get_all_positions()

    def get_open_position(self, symbol: str) -> Position | None:
        """
        Retrieve the open position for the specified symbol.

        Parameters:
        - symbol (str): The symbol of the asset for which the open position should be retrieved.

        Returns:
        - Position | None: The open position object for the specified symbol, or None if no position is found for the symbol.

        Raises:
        - APIError: If an error occurs while retrieving the open position from the trading client.
        """
        try:
            return self._trading_client.get_open_position(symbol)
        except APIError:  # no position for the symbol
            return None

    @override
    def order_share(
        self,
        symbol: str,
        share: int | float,
        order_type: OrderType | None = OrderType.MARKET,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        **kwargs,
    ) -> Order:
        """
        Place an order to buy or sell a specified number of shares of a given asset.

        Parameters:
        - symbol (str): The symbol of the asset.
        - share (int | float): The number of shares to be bought or sold.
        - order_type (OrderType | None): The type of the order (e.g., MARKET, LIMIT, STOP). Defaults to MARKET.
        - time_in_force (TimeInForce | None): The time in force for the order (e.g., GTC, GTD, IOC). Defaults to GTC.
        - kwargs: Additional keyword arguments for the order request.

        Returns:
        - Order: The order object if the order is successfully placed.
        """
        if isinstance(share, float) and not self.is_fractionable(symbol):
            share = int(share)

        if share == 0:
            return

        if not self.is_tradeable(symbol):
            return

        side = OrderSide.BUY if share > 0 else OrderSide.SELL
        order_request = OrderRequest(
            symbol=symbol,
            qty=abs(share),
            side=side,
            type=order_type,
            time_in_force=time_in_force,
            **kwargs,
        )
        try:
            return self._trading_client.submit_order(order_request)
        except Exception as e:
            self.logger.error(f"Error sending order: {e}")

    @override
    def order_value(
        self,
        symbol: str,
        value: float,
        order_type: OrderType | None = OrderType.MARKET,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        **kwargs,
    ):
        if value == 0:
            return

        if not self.is_tradeable(symbol):
            return

        side = OrderSide.BUY if value > 0 else OrderSide.SELL
        if self.is_fractionable(symbol):
            order_request = OrderRequest(
                symbol=symbol,
                notional=abs(value),
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                **kwargs,
            )
            return self._trading_client.submit_order(order_request)
        else:
            self.logger.warning(
                f"{symbol} is not fractionable, try placing order with the nearest quantity."
            )
            quantity = value // self.get_latest_bar(symbol).close
            return self.order_share(
                symbol, quantity, order_type, time_in_force, **kwargs
            )

    @override
    def order_percent(
        self,
        symbol: str,
        percent: float,
        order_type: OrderType | None = OrderType.MARKET,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        **kwargs,
    ):
        equity = self.get_equity()
        value = equity * percent
        return self.order_value(symbol, value, order_type, time_in_force, **kwargs)

    @override
    def order_target_share(
        self,
        symbol: str,  # The symbol of the asset.
        target_share: int | float,  # The target number of shares for the position.
        order_type: OrderType,  # The type of the order (e.g., MARKET, LIMIT, STOP).
        time_in_force: TimeInForce,  # The time in force for the order (e.g., GTC, GTD, IOC).
        **kwargs,  # Additional keyword arguments for the order request.
    ) -> Order:
        """
        Place an order to adjust the position's number of shares to a target number of shares.

        If the symbol has an open position, the function calculates the difference between the target number of shares and the current position's number of shares.
        Then, it places an order to adjust the position to the target number of shares.
        If the symbol does not have an open position, it places an order to buy or sell shares to reach the target number of shares.

        Parameters:
        - symbol (str): The symbol of the asset.
        - target_share (int | float): The target number of shares for the position.
        - order_type (OrderType): The type of the order (e.g., MARKET, LIMIT, STOP).
        - time_in_force (TimeInForce): The time in force for the order (e.g., GTC, GTD, IOC).
        - kwargs: Additional keyword arguments for the order request.

        Returns:
        - Order: The order object if the order is successfully placed.
        """
        pos = self.get_open_position(symbol)
        if pos is None:
            return self.order_share(
                symbol, target_share, order_type, time_in_force, **kwargs
            )
        else:
            current_share = pos.qty
            share_to_target = target_share - current_share
            return self.order_share(
                symbol, share_to_target, order_type, time_in_force, **kwargs
            )

    @override
    def order_target_value(
        self,
        symbol,
        target_value: float,
        order_type: OrderType,
        time_in_force: TimeInForce,
        **kwargs,
    ):
        """
        Place an order to adjust the position's value to a target value.

        If the symbol has an open position, the function calculates the difference between the target value and the current position's value.
        Then, it places an order to adjust the position to the target value.
        If the symbol does not have an open position, it places an order to buy or sell shares to reach the target value.

        Parameters:
        - symbol (str): The symbol of the asset.
        - target_value (float): The target value for the position.
        - order_type (OrderType): The type of the order (e.g., MARKET, LIMIT, STOP).
        - time_in_force (TimeInForce): The time in force for the order (e.g., GTC, GTD, IOC).
        - kwargs: Additional keyword arguments for the order request.

        Returns:
        - Order: The order object if the order is successfully placed.
        """
        pos = self.get_open_position(symbol)
        if pos is None:
            return self.order_value(
                symbol, target_value, order_type, time_in_force, **kwargs
            )
        else:
            current_value = pos.market_value
            value_to_target = target_value - current_value
            return self.order_value(
                symbol, value_to_target, order_type, time_in_force, **kwargs
            )

    @override
    def order_target_percentage(
        self,
        symbol: str,  # The symbol of the asset.
        target_percent: float,  # The target percentage for the position.
        order_type: OrderType,  # The type of the order (e.g., MARKET, LIMIT, STOP).
        time_in_force: TimeInForce,  # The time in force for the order (e.g., GTC, GTD, IOC).
        **kwargs,  # Additional keyword arguments for the order request.
    ) -> Order:
        """
        Place an order to adjust the position's value to a target value based on a percentage of the account's equity.

        If the symbol has an open position, the function calculates the difference between the target value and the current position's value.
        Then, it places an order to adjust the position to the target value.
        If the symbol does not have an open position, it places an order to buy or sell shares to reach the target value.

        Parameters:
        - symbol (str): The symbol of the asset.
        - target_percent (float): The target percentage for the position.
        - order_type (OrderType): The type of the order (e.g., MARKET, LIMIT, STOP).
        - time_in_force (TimeInForce): The time in force for the order (e.g., GTC, GTD, IOC).
        - kwargs: Additional keyword arguments for the order request.

        Returns:
        - Order: The order object if the order is successfully placed.
        """
        equity = self.get_equity()
        target_value = equity * target_percent
        return self.order_target_value(
            symbol, target_value, order_type, time_in_force, **kwargs
        )

    @override
    def get_orders(self) -> list[Order]:
        return self._trading_client.get_orders()

    @override
    def cancel_all_orders(self) -> list[CancelOrderResponse]:
        """
        Cancel all pending orders for the account.

        Parameters:
        - None

        Returns:
        - list[CancelOrderResponse]: A list of responses indicating the status of each order cancellation.
        """
        try:
            return self._trading_client.cancel_orders()
        except Exception as e:
            self.logger.error(f"Error canceling all orders: {e}")

    @override
    def close_all_positions(self, cancel_orders: bool = True) -> ClosePositionResponse:
        """
        Close all open positions for the account.

        Parameters:
        - cancel_orders (bool): A boolean flag indicating whether to cancel any pending orders for the closed positions. Defaults to True.

        Returns:
        - ClosePositionResponse: A response object containing information about the closing of the positions.
        """
        return self._trading_client.close_all_positions(cancel_orders)

    @override
    def cancel_order(self, order_id: UUID | str) -> CancelOrderResponse:
        """
        Cancel an existing order by its unique identifier.

        Parameters:
        - order_id (UUID | str): The unique identifier of the order to be cancelled. It can be either a UUID string or a string representation of the order ID.

        Returns:
        - CancelOrderResponse: A response object containing information about the cancellation status of the specified order.
        """
        return self._trading_client.cancel_order_by_id(order_id)

    @override
    def close_position(self, symbol: str) -> Order:
        """
        Close an open position for the specified symbol.

        Parameters:
        - symbol (str): The symbol of the asset for which the position should be closed.

        Returns:
        - Order: The order object representing the closing of the position.
        """
        return self._trading_client.close_position(symbol)

    def subscribe_trade_update(self, handler: Callable[[Any], None]) -> None:
        self._trading_stream.subscribe_trade_updates(handler)

    def subscribe_minute_bars(
        self, handler: Callable[[Bar], Awaitable[None]], symbols: list[str]
    ) -> None:
        self._data_stream.subscribe_bars(handler, *symbols)

    def subscribe_daily_bars(
        self, handler: Callable[[Bar], Awaitable[None]], symbols: list[str]
    ) -> None:
        self._data_stream.subscribe_daily_bars(handler, *symbols)

    def unsubscribe_minute_bars(self, symbols: list[str]) -> None:
        self._data_stream.unsubscribe_bars(*symbols)

    def unsubscribe_daily_bars(self, symbols: list[str]) -> None:
        self._data_stream.unsubscribe_daily_bars(*symbols)

    async def stream_trade(self) -> None:
        await self._trading_stream._run_forever()

    async def stream_data(self) -> None:
        await self._data_stream._run_forever()

    async def streaming(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.stream_trade())
            tg.create_task(self.stream_data())
