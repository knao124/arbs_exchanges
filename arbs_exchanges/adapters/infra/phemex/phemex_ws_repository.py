# %%
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


class PhemexWsRepository(
    IOrderBookRepository, IExecutionRepository, IPositionRepository
):
    """PhemexDataStoreのデータを型安全に取得する"""

    def __init__(self, store: pybotters.PhemexDataStore):
        self._store = store

    def fetch_order_book(self) -> OrderBook:
        orderbook_dict = self._store.orderbook.sorted()
        return _to_orderbook(orderbook_dict)

    def fetch_executions(self) -> list[Execution]:
        trade_dicts = self._store.trade.find()
        return _to_executions(trade_dicts)

    def fetch_positions(self) -> list[Position]:
        position_dicts = self._store.positions.find()
        return [_to_position(position_dict) for position_dict in position_dicts]


def _to_orderbook(orderbook_dict: dict) -> OrderBook:
    """
    wsで返ってくるデータを構造体に変換する

    {
        "asks": [
            {
                "symbol": "BTCUSDT",
                "side": "asks",
                "priceEp": "60823.5",
                "qty": "12.646",
            },
            {"symbol": "BTCUSDT", "side": "asks", "priceEp": "60824", "qty": "8.224"},
        ],
        "bids": [
            {
                "symbol": "BTCUSDT",
                "side": "bids",
                "priceEp": "60819.8",
                "qty": "22.629",
            },
            {
                "symbol": "BTCUSDT",
                "side": "bids",
                "priceEp": "60817.2",
                "qty": "19.459",
            },
        ],
    }
    """
    orderbook = {"asks": [], "bids": []}
    for key in ["asks", "bids"]:
        if key not in orderbook_dict:
            continue
        orderbook[key] = [
            OrderBookItem(
                symbol=Symbol.from_exchange_name_and_symbol("phemex", item["symbol"]),
                side_int=1 if item["side"] == "asks" else -1,
                price=float(item["priceEp"]),
                volume=float(item["qty"]),
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
            "symbol": "BTCUSDT",
            "timestamp": 1728629825001757528,
            "side": "Sell",
            "priceEp": "60772.9",
            "qty": "0.473",
        },
    ]
    """
    return [
        Execution(
            id=None,
            ts=pd.Timestamp(int(trade["timestamp"]), unit="ns"),
            symbol=Symbol.from_exchange_name_and_symbol("phemex", trade["symbol"]),
            side_int=1 if trade["side"] == "Buy" else -1,
            price=float(trade["priceEp"]),
            volume=float(trade["qty"]),
        )
        for trade in trade_dicts
    ]


def _to_position(position_dict: dict) -> Position:
    """
    wsで返ってくるデータを構造体に変換する

    position_dictの中身は以下のようになっている。
    {
        "accountID": 10063930003,
        "assignedPosBalanceRv": "6.125269388",
        "avgEntryPriceRp": "60841.4",
        "bankruptCommRv": "0.0363168234",
        "bankruptPriceRp": "0.1",
        "buyLeavesQty": "0",
        "buyLeavesValueRv": "0",
        "buyValueToCostRr": "0.10114",
        "createdAtNs": 0,
        "crossSharedBalanceRv": "1989.092992592",
        "cumClosedPnlRv": "-0.3787",
        "cumFundingFeeRv": "0",
        "cumPtFeeRv": "0",
        "cumTransactFeeRv": "4.40303802",
        "curTermDiscountFeeRv": "0",
        "curTermPtFeeRv": "0",
        "curTermRealisedPnlRv": "-0.03650484",
        "currency": "USDT",
        "dataVer": 50,
        "deleveragePercentileRr": "0",
        "displayLeverageRr": "10.00570326",
        "estimatedOrdLossRv": "0",
        "execSeq": 23669226521,
        "freeCostRv": "0",
        "freeQty": "-0.001",
        "initMarginReqRr": "0.1",
        "lastFundingTime": 1728604800000000000,
        "lastTermEndTime": 1728628028916543455,
        "leverageRr": "-10",
        "liquidationPriceRp": "0.1",
        "maintMarginReqRr": "0.005",
        "makerFeeRateRr": "-1",
        "markPriceRp": "60832.2",
        "minPosCostRv": "0.34066032",
        "orderCostRv": "0",
        "posCostRv": "6.116069388",
        "posMode": "OneWay",
        "posSide": "Merged",
        "positionMarginRv": "6.0797525646",
        "positionStatus": "Normal",
        "riskLimitIndexId": 1002,
        "riskLimitRv": "20000000",
        "sellLeavesQty": "0",
        "sellLeavesValueRv": "0",
        "sellValueToCostRr": "0.10126",
        "side": "Buy",
        "size": "0.001",
        "symbol": "BTCUSDT",
        "takerFeeRateRr": "-1",
        "term": 9,
        "transactTimeNs": 1728630804128655056,
        "unrealisedPnlRv": "-0.0092",
        "updatedAtNs": 0,
        "usedBalanceRv": "6.116069388",
        "userID": 1006393,
        "valueRv": "60.8414",
    }
    """

    side_int = 1 if position_dict["side"] == "Buy" else -1
    return Position(
        symbol=Symbol.from_exchange_name_and_symbol("phemex", position_dict["symbol"]),
        entry_price=Decimal(position_dict["avgEntryPriceRp"]),
        size_with_sign=Decimal(position_dict["size"]) * side_int,
    )
