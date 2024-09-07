import pandas as pd
import pybotters

from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook, OrderbookItem


class BybitWsRepository:
    """BybitDataStoreのデータを型安全に取得する"""

    def __init__(self, store: pybotters.BybitDataStore):
        self._store = store

    def sorted_orderbook(self) -> Orderbook:
        orderbook_dict = self._store.orderbook.sorted()
        return _to_sorted_orderbook(orderbook_dict)

    def trades(self) -> list[Execution]:
        trade_dicts = self._store.trade.find()
        return _to_executions(trade_dicts)


def _to_sorted_orderbook(orderbook_dict: dict) -> Orderbook:
    """
    wsで返ってくるデータを構造体に変換する

    orderbook_dictの中身は以下のようになっている。
    {
        "a": [
            {"s": "BTCUSDT", "S": "a", "p": "59060.10", "v": "12.314"},
            {"s": "BTCUSDT", "S": "a", "p": "59060.80", "v": "0.263"},
            ...
        ],
        "b": [
            {"s": "BTCUSDT", "S": "b", "p": "59060.00", "v": "10.641"},
            {"s": "BTCUSDT", "S": "b", "p": "59059.90", "v": "0.101"},
            ...
        ],
    }
    """
    orderbook = {}
    for key in ["a", "b"]:
        orderbook[key] = [
            OrderbookItem(
                symbol=item["s"],
                side_int=1 if item["S"] == "a" else -1,
                price=float(item["p"]),
                volume=float(item["v"]),
            )
            for item in orderbook_dict[key]
        ]
    return Orderbook(ask=orderbook["a"], bid=orderbook["b"])


def _to_executions(trade_dicts: dict) -> list[Execution]:
    """
    wsで返ってくるデータを構造体に変換する

    trade_dictの中身は以下のようになっている。
    [
        {
            "T": 1725093054120,
            "s": "BTCUSDT",
            "S": "Buy",
            "v": "0.001",
            "p": "59065.80",
            "L": "PlusTick",
            "i": "5ed00281-0d1a-54f4-85be-809e932d04b5",
            "BT": False,
        },
        ...
    ]

    """
    return [
        Execution(
            id=trade["i"],
            ts=pd.Timestamp(int(trade["T"]), unit="ms"),
            symbol=trade["s"],
            side_int=1 if trade["S"] == "Buy" else -1,
            price=float(trade["p"]),
            volume=float(trade["v"]),
        )
        for trade in trade_dicts
    ]
