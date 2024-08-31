import time
from dataclasses import dataclass

import numpy as np
import yfinance as yf


@dataclass
class _RestTickerConfig:
    symbol: str
    update_limit_sec: float


class YahooFXTicker:
    def __init__(self, symbol: str, update_limit_sec: float = 0.5):
        assert symbol in ["JPY=X"]

        self._config = _RestTickerConfig(symbol, update_limit_sec)

        self._last_price = 0
        self._last_ts = 0

    def last_price(self):
        if time.time() - self._last_ts >= self._config.update_limit_sec:
            data = yf.download(
                self._config.symbol, period="1d", interval="1m", progress=False
            )
            self._last_price = data["Close"][-1]
            self._last_ts = time.time()

        return self._last_price

    def ask_price(self):
        return self.last_price()

    def bid_price(self):
        return self.last_price()


class ITicker:
    def bid_price(self) -> int or float:
        ...

    def ask_price(self) -> int or float:
        ...

    def last_price(self) -> int or float:
        ...


class ILastPriceGetter:
    def last_price(self) -> int or float:
        ...


class TickerInUSD:
    def __init__(self, coinjpy_ticker: ITicker, usdjpy_ticker: ILastPriceGetter):
        self._coinjpy_ticker = coinjpy_ticker
        self._usdjpy_ticker = usdjpy_ticker

    def bid_price(self):
        return self._in_usd(self._coinjpy_ticker.bid_price())

    def ask_price(self):
        return self._in_usd(self._coinjpy_ticker.ask_price())

    def last_price(self):
        return self._in_usd(self._coinjpy_ticker.last_price())

    def _in_usd(self, price: float or int):
        return np.round(price / self._usdjpy_ticker.last_price(), 2)


class TickerInJPY:
    def __init__(self, coinusd_ticker: ITicker, usdjpy_ticker: ILastPriceGetter):
        self._coinusd_ticker = coinusd_ticker
        self._usdjpy_ticker = usdjpy_ticker

    def bid_price(self):
        return self._in_jpy(self._coinusd_ticker.bid_price())

    def ask_price(self):
        return self._in_jpy(self._coinusd_ticker.ask_price())

    def last_price(self):
        return self._in_jpy(self._coinusd_ticker.last_price())

    def _in_jpy(self, price: float or int):
        return np.round(price * self._usdjpy_ticker.last_price(), 2)
