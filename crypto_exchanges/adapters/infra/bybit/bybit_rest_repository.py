from decimal import Decimal
from logging import getLogger
from typing import Optional

import ccxt
import pandas as pd

from arbs_exchanges.core.domain.entities import (
    Balance,
    Execution,
    Fee,
    OrderBook,
    OrderBookItem,
    Position,
    Symbol,
)
from arbs_exchanges.core.domain.repositories import (
    IBalanceRepository,
    IExecutionRepository,
    IFeeRepository,
    IOrderBookRepository,
    IPositionRepository,
)


class BybitRestRepository(
    IOrderBookRepository,
    IExecutionRepository,
    IFeeRepository,
    IBalanceRepository,
    IPositionRepository,
):
    def __init__(self, ccxt_exchange: ccxt.Exchange, update_interval_sec: float):
        self._ccxt_exchange = ccxt_exchange
        self._update_interval_sec = update_interval_sec  # TODO: 実装

        self._logger = getLogger(__name__)

    def _to_category(self, symbol: Symbol) -> str:
        """Bybitのカテゴリを返す. 通貨ペアによって変わる

        Args:
            symbol (Symbol): 通貨ペア

        Raises:
            ValueError: 通貨ペアが不正な場合

        Returns:
            str: カテゴリ
        """
        if symbol == Symbol.BYBIT_LINEAR_BTCUSDT:
            return "linear"
        raise ValueError(f"Invalid symbol: {symbol}")

    def fetch_order_book(
        self,
        symbol: Symbol,
        limit: Optional[int] = None,
    ) -> OrderBook:
        orderbook_dict = self._ccxt_exchange.fetch_order_book(
            symbol=symbol.value,
            limit=limit,
            params={"category": self._to_category(symbol)},
        )
        return _to_orderbook(orderbook_dict, symbol)

    def fetch_executions(
        self,
        symbol: Symbol,
        limit: Optional[int] = None,
    ) -> list[Execution]:
        trades = self._ccxt_exchange.fetch_trades(symbol=symbol.value, limit=limit)
        return _to_executions(trades, symbol)

    def fetch_positions(
        self,
        symbol: Symbol,
    ) -> list[Position]:
        position_dicts = self._ccxt_exchange.fetch_positions(
            # see: https://bybit-exchange.github.io/docs/v5/position
            symbols=[symbol.value],
            params={"category": self._to_category(symbol)},
        )
        positions = []
        for position_dict in position_dicts:
            self._logger.info(position_dict)
            positions.append(_to_position(position_dict, symbol))
        return positions

    def fetch_balance(self) -> Balance:
        resp = self._ccxt_exchange.fetch_balance()
        return _to_balance(resp)

    def fetch_fee(
        self,
        symbol: Symbol,
    ) -> Fee:
        self._ccxt_exchange.load_markets()
        fee_dict = self._ccxt_exchange.markets[symbol.value]
        return _to_fee(fee_dict, symbol)


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


def _to_executions(trade_dicts: list[dict], symbol: Symbol) -> list[Execution]:
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
            symbol=symbol,
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


def _to_fee(fee_dict: dict, symbol: Symbol) -> Fee:
    """ccxtのfetch_feeの返り値をFeeに変換する

    fee_dictの中身は以下のようになっている。
    {
        "maker": "0.0002",
        "taker": "0.0004",
    }

    Args:
        fee_dict (dict): ccxtのfetch_feeの返り値

    Returns:
        Fee: Fee
    """
    return Fee(
        symbol=symbol,
        maker=Decimal(str(fee_dict["maker"])),
        taker=Decimal(str(fee_dict["taker"])),
    )


def _to_position(position_dict: dict, symbol: Symbol) -> Position:
    """ccxtのfetch_positionsの返り値をPositionに変換する

    position_dictの中身は以下のようになっている。
    {
        "info": {
            "symbol": "BTCUSDT",
            "leverage": "10",
            "autoAddMargin": "0",
            "avgPrice": "61748.39486486",
            "liqPrice": "69304.50300242",
            "riskLimitValue": "2000000",
            "takeProfit": "",
            "positionValue": "22846.9061",
            "isReduceOnly": False,
            "tpslMode": "Full",
            "riskId": "1",
            "trailingStop": "0",
            "unrealisedPnl": "-20.6109",
            "markPrice": "61804.1",
            "adlRankIndicator": "5",
            "cumRealisedPnl": "-103.06852395",
            "positionMM": "128.0569087",
            "createdTime": "1727652674337",
            "positionIdx": "0",
            "positionIM": "2298.5129882",
            "seq": "9367100140",
            "updatedTime": "1728099583129",
            "side": "Sell",
            "bustPrice": "",
            "positionBalance": "0",
            "leverageSysUpdatedTime": "",
            "curRealisedPnl": "-12.56579837",
            "size": "0.37",
            "positionStatus": "Normal",
            "mmrSysUpdatedTime": "",
            "stopLoss": "",
            "tradeMode": "0",
            "sessionAvgPrice": "",
            "nextPageCursor": "BTCUSDT%2C1728099583129%2C0",
        },
        "id": None,
        "symbol": "BTC/USDT:USDT",
        "timestamp": 1727652674337,
        "datetime": "2024-09-29T23:31:14.337Z",
        "lastUpdateTimestamp": 1728099583129,
        "initialMargin": 2284.69060999982,
        "initialMarginPercentage": 0.09999999999999212,
        "maintenanceMargin": None,
        "maintenanceMarginPercentage": None,
        "entryPrice": 61748.39486486,
        "notional": 22846.9061,
        "leverage": 10.0,
        "unrealizedPnl": -20.6109,
        "realizedPnl": None,
        "contracts": 0.37,
        "contractSize": 1.0,
        "marginRatio": None,
        "liquidationPrice": 69304.50300242,
        "markPrice": 61804.1,
        "lastPrice": None,
        "collateral": 0.0,
        "marginMode": None,
        "side": "short",
        "percentage": None,
        "stopLossPrice": None,
        "takeProfitPrice": None,
    }
    """
    side_int = 1 if position_dict["side"] == "long" else -1
    size_abs = Decimal(str(position_dict["contracts"]))
    if size_abs == 0:
        entry_price = Decimal("nan")
    else:
        entry_price = Decimal(position_dict["entryPrice"])
    return Position(
        symbol=symbol,
        entry_price=entry_price,
        size_with_sign=size_abs * side_int,
    )
