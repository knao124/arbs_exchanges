import time
from dataclasses import dataclass
from typing import Optional, Protocol

from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook


class IRestRepository(Protocol):
    def fetch_order_book(
        self, symbol: str, limit: Optional[int] = None
    ) -> Orderbook: ...

    def fetch_trades(
        self, symbol: str, limit: Optional[int] = None
    ) -> list[Execution]: ...


@dataclass
class _RestTickerConfig:
    symbol: str
    update_limit_sec: float


class RestTicker:
    def __init__(
        self,
        repository: IRestRepository,
        symbol: str,
        update_limit_sec: float,
    ):
        self._repository = repository
        self._config = _RestTickerConfig(
            symbol=symbol,
            update_limit_sec=update_limit_sec,
        )

        self._last_ts1 = 0.0
        self._last_ts2 = 0.0
        self._last_price = 0.0
        self._last_bid = 0.0
        self._last_ask = 0.0

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
                return (self.ask_price() + self.bid_price()) * 0.5
            self._last_price = trades[0].price
            self._last_ts1 = time.time()
        return self._last_price

    def _get_bid_ask(self) -> tuple:
        if time.time() - self._last_ts2 >= self._config.update_limit_sec:
            orderbook = self._repository.fetch_order_book(
                symbol=self._config.symbol, limit=1
            )
            if len(orderbook.bid) == 0 or len(orderbook.ask) == 0:
                return self._last_bid, self._last_ask
            self._last_bid = orderbook.bid[0].price
            self._last_ask = orderbook.ask[0].price
            self._last_ts2 = time.time()
        return self._last_bid, self._last_ask
