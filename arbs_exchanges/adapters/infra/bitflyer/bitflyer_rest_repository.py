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


class BitflyerRestRepository(
    IOrderBookRepository,
    IExecutionRepository,
    IFeeRepository,
    IBalanceRepository,
    IPositionRepository,
):
    def __init__(self, ccxt_exchange: ccxt.bitflyer, update_interval_sec: float):
        assert isinstance(ccxt_exchange, ccxt.bitflyer)

        self._ccxt_exchange = ccxt_exchange
        self._update_interval_sec = update_interval_sec  # TODO: 実装

        self._logger = getLogger(__name__)

    def fetch_order_book(
        self,
        symbol: Symbol,
        limit: Optional[int] = None,
    ) -> OrderBook:
        orderbook_dict = self._ccxt_exchange.fetch_order_book(
            symbol=symbol.value,
            limit=limit,
        )
        return _to_orderbook(orderbook_dict, symbol)

    def fetch_executions(
        self,
        symbol: Symbol,
        limit: Optional[int] = None,
    ) -> list[Execution]:
        trades = self._ccxt_exchange.fetch_trades(
            symbol=symbol.value,
            limit=limit,
        )
        return _to_executions(trades, symbol)

    def fetch_positions(
        self,
        symbol: Symbol,
    ) -> list[Position]:
        # ccxt が fetch_positions にバグがあって使えないので、product_codeを自前で書き換えている
        if symbol == Symbol.BITFLYER_CFD_BTCJPY:
            # see: https://lightning.bitflyer.com/docs
            # `各APIで使用する BTC-CFD/JPY の product_code は FX BTC/JPY の product_code を引き継ぎ、 FX_BTC_JPYとします`
            product_code = "FX_BTC_JPY"
        else:
            raise ValueError(f"Invalid symbol: {symbol}")
        position_dicts = self._ccxt_exchange.fetch_positions(
            symbols=[symbol.value],
            params={"product_code": product_code},
        )
        positions = []
        for position_dict in position_dicts:
            positions.append(_to_position(position_dict, symbol))
        return positions

    def fetch_balance(self) -> Balance:
        # 資産の残高を取得
        res = self._ccxt_exchange.fetch_balance()
        balance = _to_balance(res)

        # 証拠金を取得
        res = self._ccxt_exchange.private_get_getcollateral()
        """
        以下のようなdictが返される。 証拠金は Balanceじゃなくて Collateral で取得できる

        {'collateral': '183643.000000000000',
        'open_position_pnl': '0.0',
        'require_collateral': '88000.0',
        'keep_rate': '2.0868522727272727272727272727',
        'margin_call_amount': '0.0',
        'margin_call_due_date': None}

        see: https://lightning.bitflyer.com/docs?lang=en#get-margin-status
        """
        # 証拠金を足す
        balance.balance_in_jpy += float(res["collateral"])

        return balance

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


def _to_fee(fee_dict: dict, symbol: str) -> Fee:
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


def _to_position(position_dict: dict, symbol: str) -> Position:
    """ccxtのfetch_positionsの返り値をPositionに変換する

    position_dictの中身は以下のようになっている。
    {
        "product_code": "FX_BTC_JPY",
        "side": "BUY",
        "price": "9247803.0",
        "size": "0.01",
        "commission": "0.0",
        "swap_point_accumulate": "0.0",
        "require_collateral": "46164.995",
        "open_date": "2024-10-06T08:22:37.6469062Z",
        "leverage": "2.000000000000",
        "pnl": "1.70000000000000",
        "sfd": "0.0",
    }
    """
    side_int = 1 if position_dict["side"] == "BUY" else -1
    size_abs = Decimal(str(position_dict["size"]))
    if size_abs == 0:
        entry_price = Decimal("nan")
    else:
        entry_price = Decimal(position_dict["price"])
    return Position(
        symbol=symbol,
        entry_price=entry_price,
        size_with_sign=size_abs * side_int,
    )
