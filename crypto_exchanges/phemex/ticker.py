import time
from dataclasses import dataclass

import ccxt


@dataclass
class _RestTickerConfig:
    symbol: str
    update_limit_sec: float = 0.5


class PhemexRestTicker:
    def __init__(
        self, ccxt_exchange: ccxt.phemex, symbol: str, update_limit_sec: float = 0.5
    ):

        self._phemex = ccxt_exchange
        self._config = _RestTickerConfig(
            symbol=symbol, update_limit_sec=update_limit_sec
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
            trades = self._phemex.fetch_trades(symbol=self._config.symbol, limit=1)
            self._last_price = trades[0]["price"]
            self._last_ts1 = time.time()
        return self._last_price

    def _get_bid_ask(self) -> tuple:
        if time.time() - self._last_ts2 >= self._config.update_limit_sec:
            ret = self._phemex.fetch_order_book(symbol=self._config.symbol, limit=1)
            self._last_bid = ret["bids"][0][0]
            self._last_ask = ret["asks"][0][0]
            self._last_ts2 = time.time()
        return self._last_bid, self._last_ask
