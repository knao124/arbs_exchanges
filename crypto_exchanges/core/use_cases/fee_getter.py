import time

import ccxt

from crypto_exchanges.core.domain.interfaces import IFeeRepository


class FeeGetter:
    def __init__(
        self,
        repository: IFeeRepository,
        update_limit_sec: float = 60,
    ):
        self._repository = repository
        self._update_limit_sec = update_limit_sec

    def fetch_maker_fee(self) -> float:
        fee = self._repository.fetch_fee()
        return fee.maker

    def fetch_taker_fee(self) -> float:
        fee = self._repository.fetch_fee()
        return fee.taker


# 参考に残しておく
class BybitFeeGetter:
    def __init__(
        self,
        ccxt_exchange: ccxt.bybit,
        symbol: str,
        update_limit_sec: float = 60,
    ):
        self._bybit = ccxt_exchange
        if symbol == "BTCUSDT":
            self.symbol = "BTC/USDT:USDT"
        elif symbol == "ETHUSDT":
            self.symbol = "ETH/USDT:USDT"
        else:
            raise ValueError(f"{symbol} not supported")

        self._last_maker_ts = 0.0
        self._last_taker_ts = 0.0
        self._last_maker_fee = 0.0
        self._last_taker_fee = 0.0
        self.update_limit_sec = update_limit_sec

    def fetch_maker_fee(self) -> float:
        self._bybit.load_markets()
        return self._bybit.markets[self.symbol]["maker"]

    def fetch_taker_fee(self) -> float:
        self._bybit.load_markets()
        return self._bybit.markets[self.symbol]["taker"]

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
