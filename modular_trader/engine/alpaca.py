from __future__ import annotations

import asyncio
import gc
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
from pydantic import BaseModel  # field_validator,; PrivateAttr,; SecretStr,
from pydantic import ConfigDict, Field, model_validator

# from pydantic.dataclasses import dataclass
from typing_extensions import override

from modular_trader.common.enums import TradingMode
from modular_trader.logging import BaseLogger, TradingLogger

from .base import BaseEngine

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    import pandas as pd


def get_api_key() -> str | None:
    """
    Retrieves the Alpaca API key from the "ALPACA_API_KEY" environment variable.

    Returns:
        str | None: The Alpaca API key, or None if not set.
    """

    key = os.environ.get("ALPACA_API_KEY", None)
    if key is None:
        raise ValueError("ALPACA_API_KEY environment variable not set")
    return key


def get_secret_key() -> str | None:
    """
    Retrieves the Alpaca API secret key from the "ALPACA_SECRET_KEY" environment variable.

    Returns:
        str | None: The Alpaca API secret key, or None if not set.
    """
    key = os.environ.get("ALPACA_SECRET_KEY")
    if key is None:
        raise ValueError("ALPACA_SECRET_KEY environment variable not set")
    return key


# @dataclass(config=ConfigDict(arbitrary_types_allowed=True, extra="forbid"))
class AlpacaEngine(BaseEngine, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # api_key: str = Field(default_factory=get_api_key)
    # secret_key: str = Field(default_factory=get_secret_key)
    mode: TradingMode = Field(default=TradingMode.PAPER)
    asset_class: AssetClass = Field(default=AssetClass.US_EQUITY)
    feed: DataFeed | CryptoFeed | OptionsFeed | None = Field(default=None)
    logger: BaseLogger = Field(default_factory=TradingLogger)
    # api_key: SecretStr = Field(default_factory=get_api_key)
    # secret_key: SecretStr = Field(default_factory=get_secret_key)
    # _trading_client: TradingClient = PrivateAttr(default_factory=lambda: None)
    # _trading_stream: TradingStream = PrivateAttr(default_factory=lambda: None)
    # _data_client: (
    #     StockHistoricalDataClient
    #     | CryptoHistoricalDataClient
    #     | OptionHistoricalDataClient
    # ) = PrivateAttr(default_factory=lambda: None)
    # _data_stream: StockDataStream | CryptoDataStream | OptionDataStream = PrivateAttr(
    #     default_factory=lambda: None
    # )

    # is_paper: bool = property(fget=lambda self: self.mode == TradingMode.PAPER)

    @property
    def is_paper(self) -> bool:
        """
        Checks if the engine is in paper trading mode.

        Returns:
            bool: True if in paper trading mode, False otherwise.
        """
        return self.mode == TradingMode.PAPER

    # @field_validator("api_key", mode="before")
    # @classmethod
    # def _api_key(cls, v: str | None) -> str:
    #     """validate api key"""
    #     if v is None:
    #         raise ValueError("API key not found")
    #     return v

    # @field_validator("secret_key", mode="before")
    # @classmethod
    # def _secret_key(cls, v: str | None) -> str:
    #     """validate secret key"""
    #     if v is None:
    #         raise ValueError("SECRET key not found")
    #     return v

    @model_validator(mode="after")
    def _initialize(self):
        """
        Initialize trading and data clients and streams.

        This method is called after the model is validated and initialized.
        It sets up the Alpaca trading and data clients and streams using the
        API key and secret key stored in the environment variables.
        """
        _api_key = get_api_key()
        _secret_key = get_secret_key()
        self._init_trading(_api_key, _secret_key)
        self._init_data(_api_key, _secret_key)
        self._init_assets()

    # def __post_init__(self):
    #     self._init_trading()
    #     self._init_data()
    #     self._init_assets()

    async def _close_websocket(self):
        """
        Close the Alpaca trading and data streams.

        This method is called by the destructor to ensure that the streams are
        closed when the object is garbage collected.
        """
        self.logger.debug(f"{self.__class__.__name__} | Closing websocket")
        self._trading_stream.close()
        self._data_stream.close()

    def __del__(self) -> None:
        """
        Destructor for the AlpacaEngine class.

        This method is called when the object is garbage collected. It
        closes the Alpaca trading and data streams, and deletes the
        clients and streams to free up memory.
        """
        self.logger.debug(f"{self.__class__.__name__} | Destructor Called")
        asyncio.run(self._close_websocket)
        del (
            self._data_client,
            self._data_stream,
            self._trading_client,
            self._trading_stream,
        )
        gc.collect()

    def _init_trading(self, _api_key: str, _secret_key: str) -> None:
        """Initializes the Alpaca trading client and stream.

        This method takes in the API key and secret key as arguments and
        initializes the Alpaca trading client and stream with the given
        credentials. The `paper` argument is set to `True` if the engine is in
        paper trading mode.

        Args:
            _api_key (str): The API key for the Alpaca trading client and
                stream.
            _secret_key (str): The secret key for the Alpaca trading client
                and stream.
        """
        self.logger.debug(f"{self.__class__.__name__} | Initializing trading client")
        self._trading_client = TradingClient(
            api_key=_api_key, secret_key=_secret_key, paper=self.is_paper
        )
        self._trading_stream = TradingStream(
            api_key=_api_key, secret_key=_secret_key, paper=self.is_paper
        )

    def _init_assets(self) -> dict[str, Asset]:
        """Initialize the assets dictionary.

        This method retrieves all active assets for the specified asset_class
        using the Alpaca trading client and stores them in the _assets
        dictionary. The keys are the symbol names and the values are the Asset
        objects.

        Returns:
            dict[str, Asset]: The assets dictionary.
        """
        assets: list = self._trading_client.get_all_assets(
            filter=GetAssetsRequest(
                status=AssetStatus.ACTIVE, asset_class=self.asset_class
            )
        )
        self._assets = {x.symbol: x for x in assets}

    def _init_data(self, _api_key: str, _secret_key: str) -> None:
        """Initializes the data clients for the specified asset class.

        This method takes in the API key and secret key as arguments and
        initializes the data clients for the specified asset class using the
        Alpaca trading client.

        Args:
            _api_key (str): The API key for the Alpaca trading client and
                stream.
            _secret_key (str): The secret key for the Alpaca trading client
                and stream.

        Raises:
            ValueError: If the asset class is not supported.
        """
        match self.asset_class:
            case AssetClass.US_EQUITY:
                self._init_stock_data(_api_key, _secret_key)
            case AssetClass.CRYPTO:
                self._init_crypto_data(_api_key, _secret_key)
            case AssetClass.US_OPTION:
                self._init_option_data(_api_key, _secret_key)
            case _:
                raise ValueError("Unsupported asset class")

    def _init_stock_data(self, _api_key: str, _secret_key: str) -> None:
        """Initializes the stock data clients.

        This method takes in the API key and secret key as arguments and
        initializes the stock historical data client and stream using the
        Alpaca trading client.

        Args:
            _api_key (str): The API key for the Alpaca trading client and
                stream.
            _secret_key (str): The secret key for the Alpaca trading client
                and stream.
        """
        self.logger.debug(f"{self.__class__.__name__} | Initializing stock data")
        self.feed = self.feed or DataFeed.IEX
        self._data_client = StockHistoricalDataClient(
            api_key=_api_key, secret_key=_secret_key
        )
        self._data_stream = StockDataStream(
            api_key=_api_key, secret_key=_secret_key, feed=self.feed
        )

    def _init_crypto_data(self, _api_key: str, _secret_key: str) -> None:
        """Initializes the crypto data clients.

        This method takes in the API key and secret key as arguments and
        initializes the crypto historical data client and stream using the
        Alpaca trading client.

        Args:
            _api_key (str): The API key for the Alpaca trading client and
                stream.
            _secret_key (str): The secret key for the Alpaca trading client
                and stream.
        """
        self.logger.debug(f"{self.__class__.__name__} | Intializing crypto data")
        self.feed = self.feed or CryptoFeed.US
        self._data_client = CryptoHistoricalDataClient(
            api_key=_api_key, secret_key=_secret_key
        )
        self._data_stream = CryptoDataStream(
            api_key=_api_key, secret_key=_secret_key, feed=self.feed
        )

    def _init_option_data(self, _api_key: str, _secret_key: str) -> None:
        """Initializes the option data clients.

        This method takes in the API key and secret key as arguments and
        initializes the option historical data client and stream using the
        Alpaca trading client.

        Args:
            _api_key (str): The API key for the Alpaca trading client and
                stream.
            _secret_key (str): The secret key for the Alpaca trading client
                and stream.
        """
        self.logger.debug("Initializing option data")
        self.feed = self.feed or OptionsFeed.INDICATIVE
        self._data_client = OptionHistoricalDataClient(
            api_key=_api_key, secret_key=_secret_key
        )
        self._data_stream = OptionDataStream(
            api_key=_api_key, secret_key=_secret_key, feed=self.feed
        )

    def is_tradeable(self, symbol: str) -> bool:
        """
        Checks if a given asset is tradeable.

        Args:
            symbol (str): The symbol of the asset.

        Returns:
            bool: True if the asset is tradeable, False otherwise.
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
        Checks if a given asset is fractionable.

        Args:
            symbol (str): The symbol of the asset.

        Returns:
            bool: True if the asset is fractionable, False otherwise.
        """
        asset = self._assets.get(symbol, None)
        if asset is None:
            self.logger.warning(f"Asset `{symbol}` is not found")
            return False
        else:
            return asset.fractionable

    def get_latest_bar(self, symbol: str) -> dict[str, Bar]:
        """
        Gets the latest bar for the given symbol.

        Args:
            symbol (str): The symbol of the asset.

        Returns:
            dict[str, Bar]: A dictionary containing the latest bar.

        Raises:
            NotImplementedError: If the asset class is US_OPTION.
            ValueError: If the asset class is not supported.
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
        """Returns the name of the engine, which is "Alpaca"."""

        return "Alpaca"

    @override
    def get_logger(self):
        """
        Returns the logger of the engine.

        Returns:
            BaseLogger: The logger of the engine.
        """
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
    ) -> pd.DataFrame:
        """
        Gets the historical data for the given symbols, start date, end date,
        timeframe, and adjustment.

        Args:
            symbols (str | list[str]): The symbols to get the historical data for.
            start (datetime): The start date of the historical data.
            end (datetime | None): The end date of the historical data.
                If None, the data will be fetched until the current date.
            timeframe (TimeFrame | None): The timeframe of the historical data.
                If None, the data will be fetched in the Day timeframe.
            adjustment (Adjustment | None): The adjustment of the historical data.
                If None, the data will be fetched with the ALL adjustment.

        Returns:
            pd.DataFrame: The historical data in a MultiIndex DataFrame.
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

        # MultiIndex DataFrame
        df = bars.df
        return df
        # symbols = df.index.droplevel(1).unique()
        # return {s: df.loc[s] for s in symbols}

    @override
    def get_account(self) -> TradeAccount:
        """
        Gets the account information for the Alpaca trading client.

        Returns:
            TradeAccount: The account information.
        """
        return self._trading_client.get_account()

    @override
    def get_cash(self) -> float:
        """
        Gets the current cash balance in the Alpaca account.

        Returns:
            float: The current cash balance.
        """
        account = self.get_account()
        return float(account.cash)

    @override
    def get_equity(self) -> float:
        """
        Gets the current equity in the Alpaca account.

        Returns:
            float: The current equity.
        """
        account = self.get_account()
        return float(account.equity)

    @override
    def get_positions(self) -> list[Position]:
        """
        Gets all positions held by the Alpaca account.

        Returns:
            list[Position]: The list of positions.
        """
        return self._trading_client.get_all_positions()

    def get_positions_serialize(self) -> list[dict[str, Any]]:
        """
        Gets all positions held by the Alpaca account as a list of serialized dictionaries.

        Returns:
            list[dict[str, Any]]: The list of serialized positions.
        """
        pos = self.get_positions()
        return [p.model_dump() for p in pos]

    def get_open_position(self, symbol: str) -> Position | None:
        """
        Gets the open position for the given symbol.

        Args:
            symbol (str): The symbol of the asset.

        Returns:
            Position | None: The open position if it exists, otherwise None.
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
        Places an order for a fixed number of shares of the given symbol.

        Args:
            symbol (str): The symbol of the asset to order.
            share (int | float): The number of shares to order. If the asset is not fractionable, the value will be rounded down to the nearest integer.
            order_type (OrderType, optional): The order type. Defaults to OrderType.MARKET.
            time_in_force (TimeInForce, optional): The time in force. Defaults to TimeInForce.GTC.

        Returns:
            Order: The order response from Alpaca.
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
            order_response = self._trading_client.submit_order(order_request)
            if order_response:
                self.logger.info(
                    f"{order_response.status} | {order_response.side.upper()} {order_response.symbol} x {order_response.qty}"
                )
            return order_response
        except Exception as e:
            self.logger.error(f"{symbol} | Error sending order: {e}")

    @override
    def order_value(
        self,
        symbol: str,
        value: float,
        order_type: OrderType | None = OrderType.MARKET,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        **kwargs,
    ):
        """
        Places an order for a fixed amount of money of the given symbol.

        Args:
            symbol (str): The symbol of the asset to order.
            value (float): The amount of money to order. If the asset is not fractionable, the value will be rounded down to the nearest integer.
            order_type (OrderType, optional): The order type. Defaults to OrderType.MARKET.
            time_in_force (TimeInForce, optional): The time in force. Defaults to TimeInForce.GTC.

        Returns:
            Order: The order response from Alpaca.
        """
        if value == 0:
            return

        if not self.is_tradeable(symbol):
            return

        side = OrderSide.BUY if value > 0 else OrderSide.SELL
        if self.is_fractionable(symbol):
            order_request = OrderRequest(
                symbol=symbol,
                notional=round(abs(value), 2),  # limit to 2 decimal places
                side=side,
                type=order_type,
                # TODO: stock, crypto require different time_in_force
                time_in_force=TimeInForce.DAY,  # fractional must be Day order
                **kwargs,
            )
            try:
                order_response = self._trading_client.submit_order(order_request)
                self.logger.info(
                    f"{order_response.status} | {order_response.side.upper()} {order_response.symbol} x ${order_response.notional}"
                )
                return order_response
            except Exception as e:
                self.logger.error(f"{symbol} | Error sending order: {e}")
        else:
            self.logger.warning(
                f"{symbol} is not fractionable, try placing order with the nearest quantity."
            )
            try:
                latest_close = float(self.get_latest_bar(symbol)[symbol].close)
            except Exception as e:
                self.logger.error(
                    f"{symbol} | Error while retreiving latest close: {e}"
                )
                return
            quantity = value // latest_close
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
        """
        Places an order in the specified asset corresponding to the given percent of the current portfolio value.
        percent is in decimal format; 0.5 = 50%
        """
        equity = self.get_equity()
        value = equity * percent
        return self.order_value(symbol, value, order_type, time_in_force, **kwargs)

    @override
    def order_target_share(
        self,
        symbol: str,
        target_share: int | float,
        order_type: OrderType | None = OrderType.MARKET,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        **kwargs,
    ) -> Order:
        """
        Places an order to adjust the current position in the given symbol to the target number of shares.

        If no position exists, the order will be placed as a regular order for the target number of shares.
        If a position exists, the order will be placed as a regular order for the difference between the target number of shares and the current number of shares.

        Args:
            symbol (str): The symbol of the asset to order.
            target_share (int | float): The target number of shares.
            order_type (OrderType, optional): The order type. Defaults to OrderType.MARKET.
            time_in_force (TimeInForce, optional): The time in force. Defaults to TimeInForce.GTC.

        Returns:
            Order: The order response from Alpaca.
        """
        pos = self.get_open_position(symbol)
        if pos is None:
            return self.order_share(
                symbol, target_share, order_type, time_in_force, **kwargs
            )
        else:
            current_share = float(pos.qty)
            share_to_target = target_share - current_share
            return self.order_share(
                symbol, share_to_target, order_type, time_in_force, **kwargs
            )

    @override
    def order_target_value(
        self,
        symbol,
        target_value: float,
        order_type: OrderType | None = OrderType.MARKET,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        **kwargs,
    ):
        """
        Places an order to adjust the current position in the given symbol to the target value.

        If no position exists, the order will be placed as a regular order for the target value.
        If a position exists, the order will be placed as a regular order for the difference between the target value and the current value.

        Args:
            symbol (str): The symbol of the asset to order.
            target_value (float): The target value.
            order_type (OrderType, optional): The order type. Defaults to OrderType.MARKET.
            time_in_force (TimeInForce, optional): The time in force. Defaults to TimeInForce.GTC.

        Returns:
            Order: The order response from Alpaca.
        """
        pos = self.get_open_position(symbol)
        if pos is None:
            return self.order_value(
                symbol, target_value, order_type, time_in_force, **kwargs
            )
        else:
            current_value = float(pos.market_value)
            value_to_target = target_value - current_value
            return self.order_value(
                symbol, value_to_target, order_type, time_in_force, **kwargs
            )

    @override
    def order_target_percent(
        self,
        symbol: str,
        target_percent: float,
        order_type: OrderType | None = OrderType.MARKET,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        **kwargs,
    ) -> Order:
        """
        Places an order to adjust the current position in the given symbol to the target percent of the current portfolio value.
        percent is in decimal format; 0.5 = 50%

        Args:
            symbol (str): The symbol of the asset to order.
            target_percent (float): The target percent of the portfolio value.
            order_type (OrderType, optional): The order type. Defaults to OrderType.MARKET.
            time_in_force (TimeInForce, optional): The time in force. Defaults to TimeInForce.GTC.

        Returns:
            Order: The order response from Alpaca.
        """
        equity = self.get_equity()
        target_value = equity * target_percent
        return self.order_target_value(
            symbol, target_value, order_type, time_in_force, **kwargs
        )

    @override
    def get_orders(self) -> list[Order]:
        """
        Get all active orders.

        Returns:
            list[Order]: A list of Order objects for all active orders.
        """
        return self._trading_client.get_orders()

    @override
    def cancel_all_orders(self) -> list[CancelOrderResponse]:
        """
        Cancel all active orders.

        Returns:
            list[CancelOrderResponse]: A list of CancelOrderResponse objects for all canceled orders.
        """
        try:
            return self._trading_client.cancel_orders()
        except Exception as e:
            self.logger.error(f"Error canceling all orders: {e}")

    @override
    def close_all_positions(self, cancel_orders: bool = True) -> ClosePositionResponse:
        """
        Close all open positions.

        Args:
            cancel_orders (bool, optional): If true, all open orders will also be canceled. Defaults to True.

        Returns:
            ClosePositionResponse: The response from Alpaca.
        """
        try:
            return self._trading_client.close_all_positions(cancel_orders)
        except Exception as e:
            self.logger.error(f"Error closing all positions: {e}")
            return

    @override
    def cancel_order(self, order_id: UUID | str) -> CancelOrderResponse:
        """
        Cancel an order by ID.

        Args:
            order_id (UUID | str): The order ID to cancel.

        Returns:
            CancelOrderResponse: The response from Alpaca.
        """
        try:
            return self._trading_client.cancel_order_by_id(order_id)
        except Exception as e:
            self.logger.error(f"Error canceling order {order_id}: {e}")
            return

    @override
    def cancel_orders(self, symbol: str):
        """
        Cancel all active orders for the given symbol.

        Args:
            symbol (str): The symbol for which to cancel all orders.

        Returns:
            NotImplemented: This method is not implemented.
        """
        return NotImplemented

    @override
    def close_position(self, symbol: str) -> Order:
        """
        Close a position for a given symbol.

        Args:
            symbol (str): The symbol of the asset to close.

        Returns:
            Order: The order response from Alpaca.
        """
        try:
            order_response = self._trading_client.close_position(symbol)
            if order_response:
                self.logger.info(
                    f"{order_response.status} | {order_response.side.upper()} {order_response.symbol} x {order_response.qty}"
                )
            return order_response
        except Exception as e:
            self.logger.error(f"Error closing position {symbol}: {e}")
            return

    def subscribe_trade_update(self, handler: Callable[[Any], None]) -> None:
        """
        Subscribe to trade updates.

        Args:
            handler (Callable[[Any], None]): The callback to be called when a trade update occurs.

        Returns:
            None: This function does not return a value.

        Notes:
            The callback will be passed the Bar object as an argument.
        """
        self._trading_stream.subscribe_trade_updates(handler)

    def subscribe_minute_bars(
        self, handler: Callable[[Bar], Awaitable[None]], symbols: list[str]
    ) -> None:
        """
        Subscribe to minute bars.

        Args:
            handler (Callable[[Bar], Awaitable[None]]): The callback to be called when a minute bar occurs.
            symbols (list[str]): The symbols for which to subscribe to minute bars.

        Returns:
            None: This function does not return a value.

        Notes:
            The callback will be passed the Bar object as an argument.
        """
        
        self._data_stream.subscribe_bars(handler, *symbols)

    def subscribe_daily_bars(
        self, handler: Callable[[Bar], Awaitable[None]], symbols: list[str]
    ) -> None:
        """
        Subscribe to daily bars.

        Args:
            handler (Callable[[Bar], Awaitable[None]]): The callback to be called when a daily bar occurs.
            symbols (list[str]): The symbols for which to subscribe to daily bars.

        Returns:
            None: This function does not return a value.

        Notes:
            The callback will be passed the Bar object as an argument.
        """
        self._data_stream.subscribe_daily_bars(handler, *symbols)

    def unsubscribe_minute_bars(self, symbols: list[str]) -> None:
        """
        Unsubscribe from minute bars.

        Args:
            symbols (list[str]): The symbols for which to unsubscribe from minute bars.

        Returns:
            None: This function does not return a value.

        Notes:
            This will stop the callback from being called on minute bars.
        """
        self._data_stream.unsubscribe_bars(*symbols)

    def unsubscribe_daily_bars(self, symbols: list[str]) -> None:
        """
        Unsubscribe from daily bars.

        Args:
            symbols (list[str]): The symbols for which to unsubscribe from daily bars.

        Returns:
            None: This function does not return a value.

        Notes:
            This will stop the callback from being called on daily bars.
        """
        self._data_stream.unsubscribe_daily_bars(*symbols)

    async def stream_trade(self) -> None:
        """
        Run the trading stream.

        This method will block until the program is stopped and will run the trading stream
        in an infinite loop. The trading stream will call the callback function passed to
        `subscribe_trade_update` with the trade update data.

        Returns:
            None: This function does not return a value.

        Notes:
            This will block the current task, so you should run this in an asyncio task.
        """
        await self._trading_stream._run_forever()

    async def stream_data(self) -> None:
        """
        Run the data stream.

        This method will block until the program is stopped and will run the data stream
        in an infinite loop. The data stream will call the callback function passed to
        `subscribe_minute_bars` and `subscribe_daily_bars` with the respective data.

        Returns:
            None: This function does not return a value.

        Notes:
            This will block the current task, so you should run this in an asyncio task.
        """
        await self._data_stream._run_forever()

    async def streaming(self) -> None:
        """
        Run the trading and data streams in an infinite loop.

        This method will block until the program is stopped and will run the trading
        and data streams in an infinite loop. The trading stream will call the callback
        function passed to `subscribe_trade_update` with the trade update data.
        The data stream will call the callback function passed to `subscribe_minute_bars`
        and `subscribe_daily_bars` with the respective data.

        Returns:
            None: This function does not return a value.

        Notes:
            This will block the current task, so you should run this in an asyncio task.
        """
        self.logger.debug(f"{self.__class__.__name__} | Setting up streaming")
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.stream_trade())
            tg.create_task(self.stream_data())
