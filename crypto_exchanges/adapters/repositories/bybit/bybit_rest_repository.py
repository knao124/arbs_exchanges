from typing import Optional

import ccxt
import pandas as pd

from crypto_exchanges.core.domain.entities import (
    Balance,
    Execution,
    OrderBook,
    OrderBookItem,
)
from crypto_exchanges.core.domain.interfaces import (
    IExecutionRepository,
    IOrderBookRepository,
)


class BybitRestRepository(IOrderBookRepository, IExecutionRepository):
    def __init__(self, ccxt_exchange: ccxt.Exchange, update_limit_sec: float = 0.5):
        self._ccxt_exchange = ccxt_exchange
        self._update_limit_sec = update_limit_sec  # TODO: 実装

    def fetch_order_book(self, symbol: str, limit: Optional[int] = None) -> OrderBook:
        orderbook_dict = self._ccxt_exchange.fetch_order_book(
            symbol=symbol, limit=limit
        )
        return _to_orderbook(orderbook_dict, symbol)

    def fetch_trades(self, symbol: str, limit: Optional[int] = None) -> list[Execution]:
        trades = self._ccxt_exchange.fetch_trades(symbol=symbol, limit=limit)
        return _to_executions(trades)

    def fetch_balance(self) -> Balance:
        resp = self._ccxt_exchange.fetch_balance()
        return _to_balance(resp)


def _to_orderbook(orderbook_dict: dict, symbol: str) -> OrderBook:
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
                OrderBookItem(
                    symbol=symbol,
                    side_int=-1 if key == "asks" else 1,
                    price=price,
                    volume=volume,
                ),
            )
        ret[key] = orderbook_items
    return OrderBook(ask=ret["asks"], bid=ret["bids"])


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


def _to_balance(resp: dict) -> Balance:
    """ccxtのfetch_balanceの返り値をBalanceに変換する

    respの中身は以下のようになっている。
    - ref: https://docs.ccxt.com/#/?id=balance-structure
    {
        "info": {
            "retCode": "0",
            "retMsg": "OK",
            "result": {
                "list": [
                    {
                        "totalEquity": "156405.914164",
                        "accountIMRate": "0",
                        "totalMarginBalance": "100012.7",
                        "totalInitialMargin": "0",
                        "accountType": "UNIFIED",
                        "totalAvailableBalance": "100012.7",
                        "accountMMRate": "0",
                        "totalPerpUPL": "0",
                        "totalWalletBalance": "100012.7",
                        "accountLTV": "0",
                        "totalMaintenanceMargin": "0",
                        "coin": [
                            {
                                "availableToBorrow": "",
                                "bonus": "0",
                                "accruedInterest": "0",
                                "availableToWithdraw": "50000",
                                "totalOrderIM": "0",
                                "equity": "50000",
                                "totalPositionMM": "0",
                                "usdValue": "50007.2",
                                "unrealisedPnl": "0",
                                "collateralSwitch": True,
                                "spotHedgingQty": "0",
                                "borrowAmount": "0.000000000000000000",
                                "totalPositionIM": "0",
                                "walletBalance": "50000",
                                "cumRealisedPnl": "0",
                                "locked": "0",
                                "marginCollateral": True,
                                "coin": "USDC",
                            },
                            {
                                "availableToBorrow": "",
                                "bonus": "0",
                                "accruedInterest": "0",
                                "availableToWithdraw": "1",
                                "totalOrderIM": "0",
                                "equity": "1",
                                "totalPositionMM": "0",
                                "usdValue": "54120.930771",
                                "unrealisedPnl": "0",
                                "collateralSwitch": False,
                                "spotHedgingQty": "0",
                                "borrowAmount": "0.000000000000000000",
                                "totalPositionIM": "0",
                                "walletBalance": "1",
                                "cumRealisedPnl": "0",
                                "locked": "0",
                                "marginCollateral": True,
                                "coin": "BTC",
                            },
                            {
                                "availableToBorrow": "",
                                "bonus": "0",
                                "accruedInterest": "0",
                                "availableToWithdraw": "1",
                                "totalOrderIM": "0",
                                "equity": "1",
                                "totalPositionMM": "0",
                                "usdValue": "2272.283393",
                                "unrealisedPnl": "0",
                                "collateralSwitch": False,
                                "spotHedgingQty": "0",
                                "borrowAmount": "0.000000000000000000",
                                "totalPositionIM": "0",
                                "walletBalance": "1",
                                "cumRealisedPnl": "0",
                                "locked": "0",
                                "marginCollateral": True,
                                "coin": "ETH",
                            },
                            {
                                "availableToBorrow": "",
                                "bonus": "0",
                                "accruedInterest": "0",
                                "availableToWithdraw": "50000",
                                "totalOrderIM": "0",
                                "equity": "50000",
                                "totalPositionMM": "0",
                                "usdValue": "50005.5",
                                "unrealisedPnl": "0",
                                "collateralSwitch": True,
                                "spotHedgingQty": "0",
                                "borrowAmount": "0.000000000000000000",
                                "totalPositionIM": "0",
                                "walletBalance": "50000",
                                "cumRealisedPnl": "0",
                                "locked": "0",
                                "marginCollateral": True,
                                "coin": "USDT",
                            },
                        ],
                    }
                ]
            },
            "retExtInfo": {},
            "time": "1725754584140",
        },
        "timestamp": 1725754584140,
        "datetime": "2024-09-08T00:16:24.140Z",
        "USDC": {"free": 50000.0, "used": 0.0, "total": 50000.0, "debt": 0.0},
        "BTC": {"free": 1.0, "used": 0.0, "total": 1.0, "debt": 0.0},
        "ETH": {"free": 1.0, "used": 0.0, "total": 1.0, "debt": 0.0},
        "USDT": {"free": 50000.0, "used": 0.0, "total": 50000.0, "debt": 0.0},
        "free": {"USDC": 50000.0, "BTC": 1.0, "ETH": 1.0, "USDT": 50000.0},
        "used": {"USDC": 0.0, "BTC": 0.0, "ETH": 0.0, "USDT": 0.0},
        "total": {"USDC": 50000.0, "BTC": 1.0, "ETH": 1.0, "USDT": 50000.0},
        "debt": {"USDC": 0.0, "BTC": 0.0, "ETH": 0.0, "USDT": 0.0},
    }
    """

    return Balance(
        balance_in_btc=_safe_get(resp, ["BTC", "total"], 0.0),
        balance_in_eth=_safe_get(resp, ["ETH", "total"], 0.0),
        balance_in_jpy=_safe_get(resp, ["JPY", "total"], 0.0),
        balance_in_usd=_safe_get(resp, ["USD", "total"], 0.0),
        balance_in_usdt=_safe_get(resp, ["USDT", "total"], 0.0),
        balance_in_usdc=_safe_get(resp, ["USDC", "total"], 0.0),
    )


def _safe_get(
    d: dict,
    keys: list[str],
    default: float,
) -> float:
    """nestしているdictからsafeに値を取り出す
    dict[key1][key2][key3]...[keyN]のような形で取り出したい値があるときに使う.

    Args:
        d (dict): dict
        keys (list[str]): 取り出したい値のkeyのリスト
        default (float): 取り出したい値がない場合のデフォルト値

    Returns:
        float: 取り出した値
    """
    for key in keys:
        if not hasattr(d, "__getitem__"):
            return default
        if key not in d:
            return default
        d = d[key]
    return d
