from dataclasses import dataclass
from decimal import Decimal
from logging import getLogger

import ccxt
import numpy as np

from crypto_exchanges.core.domain.entities import Order, OrderType, Symbol
from crypto_exchanges.core.domain.repositories import IOrderRepository
from crypto_exchanges.core.use_cases.interfaces import IOrderLinkIdGenerator


class BybitOrderRepository(IOrderRepository):
    """
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.bybit,
        order_link_id_generator: IOrderLinkIdGenerator,
    ):
        """CcxtOrdererのコンストラクタ

        Args:
            ccxt_exchange (ccxt.Exchange): ccxtのexchange
            order_link_id_generator (IOrderLinkIdGenerator): order_link_idを生成するインターフェース
        """
        assert isinstance(ccxt_exchange, ccxt.bybit)
        self._ccxt_exchange = ccxt_exchange
        self._order_link_id_generator = order_link_id_generator

        self._logger = getLogger(__class__.__name__)

    def _create_order(
        self,
        symbol: Symbol,
        order_type: OrderType,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:
        """注文を作成する

        Args:
            symbol (Symbol): 通貨ペア
            order_type (OrderType): 注文タイプ
            size_with_sign (Decimal): 注文量. 正負の数で指定する.
            price (Decimal): 注文価格
            post_only (bool): post_onlyかどうか

        ccxtから返却されるdictの例. これをOrderに変換して返している
        {
            "info": {
                "orderId": "1779761587192948992",
                "orderLinkId": "62b4005a-f5d7-4b4e-9a79-e9796ddd17c9",
            },
            "id": "1779761587192948992",
            "clientOrderId": "62b4005a-f5d7-4b4e-9a79-e9796ddd17c9",
            "timestamp": None,
            "datetime": None,
            "lastTradeTimestamp": None,
            "lastUpdateTimestamp": None,
            "symbol": "BTC/USDT",
            "type": None,
            "timeInForce": None,
            "postOnly": None,
            "reduceOnly": None,
            "side": None,
            "price": None,
            "stopPrice": None,
            "triggerPrice": None,
            "takeProfitPrice": None,
            "stopLossPrice": None,
            "amount": None,
            "cost": None,
            "average": None,
            "filled": None,
            "remaining": None,
            "status": None,
            "fee": None,
            "trades": [],
            "fees": [],
        }

        Returns:
            Order: 注文
        """
        order_link_id = self._order_link_id_generator.generate()
        params = {"position_idx": 0, "order_link_id": order_link_id}
        if post_only:
            params["timeInForce"] = "PO"

        side = _to_side_str(size_with_sign)
        size = abs(size_with_sign)

        res_dict = self._ccxt_exchange.create_order(
            symbol=symbol,
            type=order_type,
            side=side,
            amount=size,
            price=price,
            params=params,
        )
        if order_type == OrderType.MARKET:
            # bybitではmarket orderの際、priceはresponseに乗っていない
            res_price = Decimal("nan")
            res_size_with_sign = size_with_sign
        elif order_type == OrderType.LIMIT:
            res_price = res_dict["price"]
            res_size_with_sign = Decimal(res_dict["amount"]) * np.sign(size_with_sign)

        order = Order(
            order_type=order_type,
            order_id=res_dict["id"],
            symbol=symbol,
            size_with_sign=res_size_with_sign,
            price=res_price,
        )

        return order

    def create_market_order(
        self,
        symbol: Symbol,
        size_with_sign: Decimal,
    ) -> Order:
        """成行注文を出す

        Args:
            symbol (Symbol): 通貨ペア
            size_with_sign (Decimal): 注文量. 正負の数で指定する.

        Returns:
            Order: 注文
        """
        return self._create_order(
            symbol=symbol,
            order_type=OrderType.MARKET,
            size_with_sign=size_with_sign,
            price=Decimal("nan"),
            post_only=False,
        )

    def create_limit_order(
        self,
        symbol: Symbol,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:
        """指値注文を出す

        Args:
            symbol (Symbol): 通貨ペア
            size_with_sign (Decimal): 注文量. 正負の数で指定する.
            price (Decimal): 注文価格. 指定しない場合は nan を指定する.
            post_only (bool): post_onlyかどうか. 成行注文の場合は常に False

        Returns:
            Order: 注文
        """
        return self._create_order(
            symbol=symbol,
            order_type=OrderType.LIMIT,
            size_with_sign=size_with_sign,
            price=price,
            post_only=post_only,
        )

    def cancel_limit_order(self, symbol: Symbol, order_id: str) -> Order:
        """注文をキャンセルする

        Args:
            symbol (Symbol): 通貨ペア
            order_id (str): 注文ID

        Returns:
            Order: 注文
        """
        res_dict = self._ccxt_exchange.cancel_order(
            id=order_id,
            symbol=symbol,
        )
        # TODO: Orderに治す
        return Order(
            order_type=OrderType.LIMIT,
            order_id=res_dict["id"],
            symbol=symbol,
            size_with_sign=Decimal(res_dict["amount"]),
            price=Decimal(res_dict["price"]),
        )

    def edit_limit_order(
        self,
        symbol: Symbol,
        order_id: str,
        size_with_sign: Decimal,
        price: Decimal,
    ) -> Order:
        """注文を編集する

        Args:
            symbol (Symbol): 通貨ペア
            order_id (str): 注文ID
            size_with_sign (Decimal): 注文量. 正負の数で指定する.
            price (Decimal): 注文価格

        Returns:
            Order: 注文
        """
        side = _to_side_str(size_with_sign)
        size = abs(size_with_sign)
        return self._ccxt_exchange.edit_order(
            id=order_id,
            symbol=symbol,
            type=OrderType.LIMIT,
            side=side,
            amount=size,
            price=price,
        )

    def get_latest_orders(self, symbol: Symbol) -> list[Order]:
        """注文を取得する

        Returns:
            list[Order]: 注文のリスト
        """
        orders = self._ccxt_exchange.fetch_orders(symbol=symbol)
        return [
            Order(
                order_type=OrderType.LIMIT,
                order_id=order["id"],
                symbol=symbol,
                size_with_sign=Decimal(order["amount"]),
                price=Decimal(order["price"]),
            )
            for order in orders
        ]

    def get_open_orders(self, symbol: Symbol) -> list[Order]:
        """未決済の注文を取得する

        Returns:
            list[Order]: 未決済の注文のリスト
        """
        orders = self._ccxt_exchange.fetch_open_orders(symbol=symbol)
        return [
            Order(
                order_type=OrderType.LIMIT,
                order_id=order["id"],
                symbol=symbol,
                size_with_sign=Decimal(order["amount"]),
                price=Decimal(order["price"]),
            )
            for order in orders
        ]


def _to_side_str(side_int: int):
    """売買方向をccxtのsideの文字列に変換する

    Args:
        side_int (int): 売買方向

    Returns:
        str: ccxtのsideの文字列
    """
    if side_int > 0:
        return "buy"
    if side_int < 0:
        return "sell"
    raise ValueError(f"side_int must be 1 or -1, but {side_int=}")
