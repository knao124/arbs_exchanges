# %%
import time
from dataclasses import dataclass

import ccxt
import pybotters
import requests


def get_public_v1_ticker(symbol: str) -> dict:
    end_point = f"https://api.coin.z.com/public/v1/ticker?symbol={symbol}"
    response = requests.get(end_point)
    return response.json()


def get_public_v1_orderbooks(symbol: str) -> dict:
    end_point = f"https://api.coin.z.com/public/v1/orderbooks?symbol={symbol}"
    response = requests.get(end_point)
    return response.json()


def get_public_v1_trades(symbol: str, limit: int = 10) -> dict:
    end_point = (
        f"https://api.coin.z.com/public/v1/trades?symbol={symbol}&page=1&count={limit}"
    )
    response = requests.get(end_point)
    return response.json()


@dataclass
class _GmoFxRestTickerConfig:
    symbol: str
    update_limit_sec: float


class GmoFxRestTicker:
    def __init__(
        self,
        symbol: str,
        update_limit_sec: float = 0.5,
    ):
        self._config = _GmoFxRestTickerConfig(
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
            trades = get_public_v1_trades(symbol=self._config.symbol)
            self._last_price = float(trades["data"]["list"][0]["price"])
            self._last_ts1 = time.time()
        return self._last_price

    def _get_bid_ask(self) -> tuple:
        if time.time() - self._last_ts2 >= self._config.update_limit_sec:
            ret = get_public_v1_orderbooks(symbol=self._config.symbol)
            self._last_bid = float(ret["data"]["bids"][0]["price"])
            self._last_ask = float(ret["data"]["asks"][0]["price"])
            self._last_ts2 = time.time()
        return self._last_bid, self._last_ask


class gmofxWsEffectiveTicker:
    def __init__(self, store: pybotters.GMOCoinDataStore, symbol: str, amount: float):
        self._store = store
        self._amount = amount

    def _get_bid_ask(self) -> tuple:
        books = self._store.orderbookstore.sorted()
        amount = self._amount
        trade_amount = {"bids": amount, "asks": amount}
        list = ["bids", "asks"]
        last = {"bids": 0.0, "asks": 0.0}
        for l in list:
            index = 0
            max_index = len(books[l])
            while trade_amount[l] > 0:
                price = float(books[l][index]["price"])
                size = float(books[l][index]["size"])
                if trade_amount[l] > size:
                    last[l] += price * size
                    trade_amount[l] -= size
                    index += 1
                    if index == max_index:
                        last[l] /= amount - trade_amount[l]
                        break
                else:
                    last[l] += price * trade_amount[l]
                    last[l] /= amount
                    trade_amount[l] = 0
        return last["bids"], last["asks"]

    def bid_price(self) -> float:
        bid, _ = self._get_bid_ask()
        return bid

    def ask_price(self) -> float:
        _, ask = self._get_bid_ask()
        return ask

    def last_price(self) -> float:
        trades = self._store.executions.find()
        # 履歴がない場合はask bidの中央を返す
        if len(trades) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return float(trades[0]["price"])
