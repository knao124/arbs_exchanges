import time

import ccxt

from ..common import bF_Symbol


class BitflyerFeeGetter:
    def __init__(
        self,
        ccxt_exchange: ccxt.bitflyer,
        symbol: bF_Symbol,
        update_limit_sec: float = 60,
    ):  # ex. "BTC_JPY"
        self.ccxt_exchange = ccxt_exchange
        self.symbol = symbol

        self._last_maker_ts = 0.0
        self._last_taker_ts = 0.0
        self._last_maker_fee = 0.0
        self._last_taker_fee = 0.0
        self.update_limit_sec = update_limit_sec

    def fetch_maker_fee(self) -> float:
        fee = self.ccxt_exchange.fetch_trading_fee(symbol=self.symbol)
        return fee["maker"]

    def fetch_taker_fee(self) -> float:
        fee = self.ccxt_exchange.fetch_trading_fee(symbol=self.symbol)
        return fee["taker"]

    def maker_fee(self) -> float:
        if time.time() - self._last_maker_ts >= self.update_limit_sec:
            self._last_maker_fee = self.fetch_maker_fee()
            self._last_maker_ts = time.time()
        return self._last_maker_fee

    def taker_fee(self) -> float:
        if time.time() - self._last_taker_ts >= self.update_limit_sec:
            self._last_taker_fee = self.fetch_taker_fee()
            self._last_taker_ts = time.time()
        return self._last_taker_fee
