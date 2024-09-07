from typing import Optional

import ccxt
import pandas as pd

from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook, OrderbookItem


class BybitRestRepository:
    def __init__(self, ccxt_exchange: ccxt.Exchange):
        self._ccxt_exchange = ccxt_exchange

    def fetch_order_book(self, symbol: str, limit: Optional[int] = None) -> Orderbook:
        orderbook_dict = self._ccxt_exchange.fetch_order_book(
            symbol=symbol, limit=limit
        )
        return _to_orderbook(orderbook_dict, symbol)

    def fetch_trades(self, symbol: str, limit: Optional[int] = None) -> list[Execution]:
        trades = self._ccxt_exchange.fetch_trades(symbol=symbol, limit=limit)
        return _to_executions(trades)


def _to_orderbook(orderbook_dict: dict, symbol: str) -> Orderbook:
    """ccxtのfetch_order_bookの返り値をOrderbookに変換する

    orderbook_dictの中身は以下のようになっている。
    {
        "symbol": "BTCUSDT",
        "bids": [[58850.0, 1.439], [58849.7, 0.001], [58849.2, 0.001]],
        "asks": [[58850.1, 10.765], [58850.2, 0.009], [58850.4, 0.033]],
        "timestamp": 1725154755854,
        "datetime": "2024-09-01T01:39:15.854Z",
        "nonce": None,
    }

    Args:
        orderbook_dict (dict): ccxtのfetch_order_bookの返り値
        symbol (str): 通貨ペア

    Returns:
        Orderbook: Orderbook
    """
    ret = {}
    for key in ["bids", "asks"]:
        orderbook_items = []
        for item in orderbook_dict[key]:
            price = item[0]
            volume = item[1]
            orderbook_items.append(
                OrderbookItem(
                    symbol=symbol,
                    side_int=-1 if key == "asks" else 1,
                    price=price,
                    volume=volume,
                ),
            )
        ret[key] = orderbook_items
    return Orderbook(ask=ret["asks"], bid=ret["bids"])


def _to_executions(trade_dicts: list[dict]) -> list[Execution]:
    """ccxtのfetch_tradesの返り値をExecutionに変換する

    trade_dictsの中身は以下のようになっている。
    [
        {
            "id": "b0580565-ddae-5fa8-b08d-aec70e26b8fd",
            "info": {
                "execId": "b0580565-ddae-5fa8-b08d-aec70e26b8fd",
                "symbol": "BTCUSDT",
                "price": "58913.40",
                "size": "0.125",
                "side": "Buy",
                "time": "1725154021969",
                "isBlockTrade": False,
            },
            "timestamp": 1725154021969,
            "datetime": "2024-09-01T01:27:01.969Z",
            "symbol": "BTC/USDT:USDT",
            "order": None,
            "type": None,
            "side": "buy",
            "takerOrMaker": None,
            "price": 58913.4,
            "amount": 0.125,
            "cost": 7364.175,
            "fee": {"cost": None, "currency": None},
            "fees": [],
        }
    ]

    Args:
        trades (list[dict]): ccxtのfetch_tradesの返り値

    Returns:
        list[Execution]: Executionのリスト
    """
    return [
        Execution(
            id=trade["id"],
            ts=pd.to_datetime(trade["timestamp"], unit="ms"),
            # TODO: unified symbol を使うかどうか検討. 使えばここは統一的に扱える. 他のclassとの統一性がなくなるかも. 他のクラスもunified symbolを使うようにするか.
            symbol=trade["symbol"],
            side_int=1 if trade["side"] == "buy" else -1,
            price=float(trade["price"]),
            volume=float(trade["amount"]),
        )
        for trade in trade_dicts
    ]
