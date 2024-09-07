import time
from dataclasses import dataclass
from typing import Optional, Protocol

import numpy as np

from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook
from crypto_exchanges.tickers.common import get_effective_price


class IRestRepository(Protocol):
    def fetch_order_book(
        self, symbol: str, limit: Optional[int] = None
    ) -> Orderbook: ...

    def fetch_trades(
        self, symbol: str, limit: Optional[int] = None
    ) -> list[Execution]: ...


@dataclass
class _RestEffectiveTickerConfig:
    symbol: str
    target_volume: float
    update_limit_sec: float


class RestEffectiveTicker:
    def __init__(
        self,
        repository: IRestRepository,
        symbol: str,
        target_volume: float,
        update_limit_sec: float,
    ):
        self._repository = repository
        self._config = _RestEffectiveTickerConfig(
            symbol=symbol,
            update_limit_sec=update_limit_sec,
            target_volume=target_volume,
        )

        self._last_ts1 = 0.0
        self._last_ts2 = 0.0
        self._last_price = np.nan
        self._last_bid_price = np.nan
        self._last_ask_price = np.nan

    def bid_price(self) -> float:
        bid, _ = self._get_bid_ask()
        return bid

    def ask_price(self) -> float:
        _, ask = self._get_bid_ask()
        return ask

    def last_price(self) -> float:
        if time.time() - self._last_ts1 >= self._config.update_limit_sec:
            trades = self._repository.fetch_trades(symbol=self._config.symbol, limit=1)
            if len(trades) == 0:
                return self._last_price
            self._last_price = trades[0].price
            self._last_ts1 = time.time()
        return self._last_price

    def _get_bid_ask(self) -> tuple:
        if time.time() - self._last_ts2 >= self._config.update_limit_sec:
            target_volume = self._config.target_volume
            orderbook = self._repository.fetch_order_book(
                symbol=self._config.symbol, limit=1
            )
            bid_price = get_effective_price(orderbook.bid, target_volume)
            ask_price = get_effective_price(orderbook.ask, target_volume)
            self._last_bid_price = bid_price
            self._last_ask_price = ask_price
            self._last_ts2 = time.time()
        return self._last_bid_price, self._last_ask_price
