from dataclasses import dataclass
from logging import getLogger
from typing import Literal

import ccxt

from ..common import CcxtRestTicker, bF_Symbol
from .ws import MyBitflyerDataStore


class BitflyerRestTicker(CcxtRestTicker):
    def __init__(
        self,
        ccxt_exchange: ccxt.bitflyer,
        symbol: str,
        update_limit_sec: float = 0.5,
    ):
        assert type(ccxt_exchange) is ccxt.bitflyer
        super().__init__(
            ccxt_exchange=ccxt_exchange,
            symbol=symbol,
            update_limit_sec=update_limit_sec,
            logger=getLogger(__class__.__name__),
        )


@dataclass
class _BitflyerWsTickerConfig:
    symbol: str


class BitflyerWsTicker:
    def __init__(
        self,
        store: MyBitflyerDataStore,
        symbol: bF_Symbol,
    ):
        self._store = store
        self._config = _BitflyerWsTickerConfig(symbol=symbol)
        self._logger = getLogger(__class__.__name__)

    def bid_price(self) -> float:
        """
        {'SELL': [{'product_code': 'FX_BTC_JPY', 'side': 'SELL', 'price': 2835954.0,
         'size': 0.04100595}, ...], 'BUY': ...}
        """
        books = self._store.board.sorted()
        if self._config.symbol == "BTC_JPY" or self._config.symbol == "ETH_JPY":
            return float(books["BUY"][0]["price"])
        raise ValueError(f"{self._config.symbol=} not supported")

    def ask_price(self) -> float:
        books = self._store.board.sorted()
        if self._config.symbol == "BTC_JPY" or self._config.symbol == "ETH_JPY":
            return float(books["SELL"][0]["price"])
        raise ValueError(f"{self._config.symbol=} not supported")

    def last_price(self) -> float:
        trades = self._store.executions.find()
        # 履歴がない場合はask bidの中央を返す
        if len(trades) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return float(trades[-1]["price"])


@dataclass
class _BitFlyerWsEffectiveTickerConfig:
    symbol: str


class BitFlyerWsEffectiveTicker:
    def __init__(self, store: MyBitflyerDataStore, symbol: str, amount: float):
        self._store = store
        self._config = _BitFlyerWsEffectiveTickerConfig(symbol=symbol)
        self._amount = amount

    def _get_bid_ask(self) -> tuple:
        books = self._store.board.sorted()
        amount = self._amount
        trade_amount = {"BUY": amount, "SELL": amount}
        list = ["BUY", "SELL"]
        last = {"BUY": 0.0, "SELL": 0.0}
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
        return last["BUY"], last["SELL"]

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
        return float(trades[-1]["price"])
