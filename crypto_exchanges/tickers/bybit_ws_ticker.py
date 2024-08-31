from dataclasses import dataclass

import pybotters


@dataclass
class _BybitWsTickerConfig:
    symbol: str


class BybitWsTicker:
    def __init__(
        self,
        store: pybotters.BybitDataStore,
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
