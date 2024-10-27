# %%
from decimal import Decimal
from logging import getLogger

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


class BitflyerWsRepository(
    IOrderBookRepository, IExecutionRepository, IPositionRepository
):
    """BitflyerDataStoreのデータを型安全に取得する"""

    def __init__(self, store: pybotters.bitFlyerDataStore):
        self._store = store

        self._logger = getLogger(__name__)

    def fetch_order_book(self) -> OrderBook:
        orderbook_dict = self._store.board.sorted()
        return _to_orderbook(orderbook_dict)

    def fetch_executions(self) -> list[Execution]:
        trade_dicts = self._store.executions.find()
        return _to_executions(trade_dicts)

    def fetch_positions(self) -> list[Position]:

        self._logger.warning(
            "bitflyer の fetch_positions は pybotters にバグがある気がするので rest を使うほうが良さそう"
        )

        position_dicts = self._store.positions.find()
        return _to_positions(position_dicts)


def _to_orderbook(orderbook_dict: dict) -> OrderBook:
    """
    wsで返ってくるデータを構造体に変換する

    orderbook_dictの中身は以下のようになっている。
    {
        "asks": [
            {
                "product_code": "FX_BTC_JPY",
                "side": "asks",
                "price": 9241727.0,
                "size": 0.02,
            },
            {
                "product_code": "FX_BTC_JPY",
                "side": "asks",
                "price": 9243075.0,
                "size": 0.02,
            },
        ],
        "bids": [
            {
                "product_code": "FX_BTC_JPY",
                "side": "bids",
                "price": 9240402.0,
                "size": 0.03294665,
            },
            {
                "product_code": "FX_BTC_JPY",
                "side": "bids",
                "price": 9239352.0,
                "size": 0.011,
            },
        ],
    }
    """
    orderbook = {}
    for key in ["asks", "bids"]:
        orderbook[key] = [
            OrderBookItem(
                symbol=Symbol.from_exchange_name_and_symbol(
                    "bitflyer", item["product_code"]
                ),
                side_int=1 if item["side"] == "bids" else -1,
                price=Decimal(str(item["price"])),
                volume=Decimal(str(item["size"])),
            )
            for item in orderbook_dict[key]
        ]
    return OrderBook(ask=orderbook["asks"], bid=orderbook["bids"])


def _to_executions(trade_dicts: dict) -> list[Execution]:
    """
    wsで返ってくるデータを構造体に変換する

    trade_dictの中身は以下のようになっている。
    [
        {
            "product_code": "FX_BTC_JPY",
            "id": 2550059512,
            "side": "BUY",
            "price": 9245828.0,
            "size": 0.05551255,
            "exec_date": "2024-10-06T09:04:32.2458378Z",
            "buy_child_order_acceptance_id": "JRF20241006-090432-013530",
            "sell_child_order_acceptance_id": "JRF20241006-090001-013365",
        }
        ...
    ]

    """
    return [
        Execution(
            id=trade["id"],
            ts=pd.Timestamp(trade["exec_date"]),
            symbol=Symbol.from_exchange_name_and_symbol(
                "bitflyer", trade["product_code"]
            ),
            side_int=1 if trade["side"] == "BUY" else -1,
            price=Decimal(str(trade["price"])),
            volume=Decimal(str(trade["size"])),
        )
        for trade in trade_dicts
    ]


def _to_positions(position_dicts: list[dict]) -> list[Position]:
    """
    wsで返ってくるデータを構造体に変換する

    position_dictの中身は以下のようになっている。
    [
        {
            "product_code": "FX_BTC_JPY",
            "side": "BUY",
            "price": 9249432.0,
            "size": 0.01,
            "commission": 0.0,
            "sfd": 0.0,
        }
    ]
    """

    positions = []
    for position_dict in position_dicts:
        symbol = Symbol.from_exchange_name_and_symbol(
            "bitflyer", position_dict["product_code"]
        )
        side_int = 1 if position_dict["side"] == "BUY" else -1
        entry_price = Decimal(str(position_dict["price"]))
        size_with_sign = Decimal(str(position_dict["size"])) * side_int

        positions.append(
            Position(
                symbol=symbol,
                entry_price=entry_price,
                size_with_sign=size_with_sign,
            )
        )

    return positions
