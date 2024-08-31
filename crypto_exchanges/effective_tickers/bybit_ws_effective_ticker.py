import time
from dataclasses import dataclass

import ccxt
import pybotters


@dataclass
class BybitWsEffectiveTickerConfig:
    symbol: str
    amount: float = 0.1


class BybitWsEffectiveTicker:
    def __init__(
        self,
        store: pybotters.BybitDataStore,
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
