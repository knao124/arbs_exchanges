import time
from dataclasses import dataclass

import ccxt
import pybotters


@dataclass
class BybitRestTickerConfig:
    symbol: str
    update_limit_sec: float = 0.5
    amount: float = 0.01


class BybitRestTicker:
    def __init__(self, ccxt_exchange: ccxt.bybit, config: BybitRestTickerConfig):
        self._bybit = ccxt_exchange
        self._config = config

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
            trades = self._bybit.fetch_trades(symbol=self._config.symbol, limit=1)
            self._last_price = trades[0]["price"]
            self._last_ts1 = time.time()
        return self._last_price

    def _get_bid_ask(self) -> tuple:
        if time.time() - self._last_ts2 >= self._config.update_limit_sec:
            ret = self._bybit.fetch_order_book(symbol=self._config.symbol, limit=1)
            self._last_bid = ret["bids"][0][0]
            self._last_ask = ret["asks"][0][0]
            self._last_ts2 = time.time()
        return self._last_bid, self._last_ask


@dataclass
class BybitRestEffectiveTickerConfig:
    symbol: str
    update_limit_sec: float = 0.5
    amount: float = 0.01


class BybitRestEffectiveTicker:
    def __init__(
        self, ccxt_exchange: ccxt.bybit, config: BybitRestEffectiveTickerConfig
    ):
        self._bybit = ccxt_exchange
        self._config = config

        self._last_ts1 = 0.0
        self._last_ts2 = 0.0
        self._last_price = 0.0
        self._last = {"bids": 0.0, "asks": 0.0}

    def bid_price(self) -> float:
        bid, _ = self._get_bid_ask()
        return bid

    def ask_price(self) -> float:
        _, ask = self._get_bid_ask()
        return ask

    def last_price(self) -> float:
        if time.time() - self._last_ts1 >= self._config.update_limit_sec:
            trades = self._bybit.fetch_trades(symbol=self._config.symbol, limit=1)
            self._last_price = trades[0]["price"]
            self._last_ts1 = time.time()
        return self._last_price

    def _get_bid_ask(self) -> tuple:
        if time.time() - self._last_ts2 >= self._config.update_limit_sec:
            # ret = self._bybit.fetch_order_book(symbol=self._config.symbol, limit=1)
            amount = self._config.amount
            ret = self._bybit.fetch_order_book(symbol=self._config.symbol, limit=1)
            trade_amount = {"bids": amount, "asks": amount}
            list = ["bids", "asks"]
            for l in list:
                index = 0
                max_index = len(ret[l])
                while trade_amount[l] > 0:
                    price = ret[l][index][0]
                    size = ret[l][index][1]
                    if trade_amount[l] > size:
                        self._last[l] += price * size
                        trade_amount[l] -= size
                        index += 1
                        if index == max_index:
                            self._last[l] /= amount - trade_amount[l]
                            break
                    else:
                        self._last[l] += price * trade_amount[l]
                        self._last[l] /= amount
                        trade_amount[l] = 0
            self._last_ts2 = time.time()
        return self._last["bids"], self._last["asks"]


@dataclass
class _BybitWsTickerConfig:
    symbol: str


class BybitWsTicker:
    def __init__(
        self,
        store: pybotters.BybitInverseDataStore or pybotters.BybitUSDTDataStore,
        symbol: str,
    ):

        self._store = store
        self._config = _BybitWsTickerConfig(symbol=symbol)

    def bid_price(self) -> float:
        books = self._store.orderbook.sorted()
        return float(books["Buy"][0]["price"])

    def ask_price(self) -> float:
        books = self._store.orderbook.sorted()
        return float(books["Sell"][0]["price"])

    def last_price(self) -> float:
        trades = self._store.trade.find()

        # 履歴がない場合はask bidの中央を返す
        if len(trades) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return float(trades[-1]["price"])


@dataclass
class BybitWsEffectiveTickerConfig:
    symbol: str
    amount: float = 0.1


class BybitWsEffectiveTicker:
    def __init__(
        self,
        store: pybotters.BybitInverseDataStore or pybotters.BybitUSDTDataStore,
        config: BybitWsEffectiveTickerConfig,
    ):

        self._store = store
        self._config = config

    def _get_bid_ask(self) -> tuple:
        last = {"Buy": 0.0, "Sell": 0.0}
        books = self._store.orderbook.sorted()
        amount = self._config.amount
        trade_amount = {"Buy": amount, "Sell": amount}
        list = ["Buy", "Sell"]
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
        return last["Buy"], last["Sell"]

    def bid_price(self) -> float:
        bid, _ = self._get_bid_ask()
        return bid

    def ask_price(self) -> float:
        _, ask = self._get_bid_ask()
        return ask

    def last_price(self) -> float:
        trades = self._store.trade.find()

        # 履歴がない場合はask bidの中央を返す
        if len(trades) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return float(trades[-1]["price"])
