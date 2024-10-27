from decimal import Decimal

import pandas as pd
import pybotters

from arbs_exchanges.core.domain.entities import (
    Execution,
    OrderBook,
    OrderBookItem,
    Position,
    Symbol,
)
from arbs_exchanges.core.domain.repositories import (
    IExecutionRepository,
    IOrderBookRepository,
    IPositionRepository,
)


class BybitWsRepository(
    IOrderBookRepository, IExecutionRepository, IPositionRepository
):
    """BybitDataStoreのデータを型安全に取得する"""

    def __init__(self, store: pybotters.BybitDataStore):
        self._store = store

    def fetch_order_book(self) -> OrderBook:
        orderbook_dict = self._store.orderbook.sorted()
        return _to_orderbook(orderbook_dict)

    def fetch_executions(self) -> list[Execution]:
        trade_dicts = self._store.trade.find()
        return _to_executions(trade_dicts)

    def fetch_positions(self) -> list[Position]:
        position_dicts = self._store.position.find()
        return [_to_position(position_dict) for position_dict in position_dicts]


def _to_orderbook(orderbook_dict: dict) -> OrderBook:
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
            OrderBookItem(
                symbol=Symbol.from_exchange_name_and_symbol("bybit", item["s"]),
                side_int=1 if item["S"] == "a" else -1,
                price=float(item["p"]),
                volume=float(item["v"]),
            )
            for item in orderbook_dict[key]
        ]
    return OrderBook(ask=orderbook["a"], bid=orderbook["b"])


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
            symbol=Symbol.from_exchange_name_and_symbol("bybit", trade["s"]),
            side_int=1 if trade["S"] == "Buy" else -1,
            price=float(trade["p"]),
            volume=float(trade["v"]),
        )
        for trade in trade_dicts
    ]


def _to_position(position_dict: dict) -> Position:
    """
    wsで返ってくるデータを構造体に変換する

    position_dictの中身は以下のようになっている。
    {
        "positionIdx": 0,
        "tradeMode": 0,
        "riskId": 1,
        "riskLimitValue": "2000000",
        "symbol": "BTCUSDT",
        "side": "Buy",
        "size": "0.001",
        "entryPrice": "62573.3",
        "sessionAvgPrice": "",
        "leverage": "10",
        "positionValue": "62.5733",
        "positionBalance": "0",
        "markPrice": "62370.78",
        "positionIM": "6.28830379",
        "positionMM": "0.34384029",
        "takeProfit": "0",
        "stopLoss": "0",
        "trailingStop": "0",
        "unrealisedPnl": "-0.20252",
        "cumRealisedPnl": "-268.71840277",
        "curRealisedPnl": "-0.03441532",
        "createdTime": "1727652674337",
        "updatedTime": "1728210481638",
        "tpslMode": "Full",
        "liqPrice": "",
        "bustPrice": "",
        "category": "linear",
        "positionStatus": "Normal",
        "adlRankIndicator": 1,
        "autoAddMargin": 0,
        "leverageSysUpdatedTime": "",
        "mmrSysUpdatedTime": "",
        "seq": 9367508781,
        "isReduceOnly": False,
    }
    """
    side_int = 1 if position_dict["side"] == "Buy" else -1
    return Position(
        symbol=Symbol.from_exchange_name_and_symbol("bybit", position_dict["symbol"]),
        entry_price=Decimal(position_dict["entryPrice"]),
        size_with_sign=Decimal(position_dict["size"]) * side_int,
    )
