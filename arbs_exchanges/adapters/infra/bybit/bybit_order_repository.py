from decimal import Decimal
from logging import getLogger
from typing import Optional

import ccxt
import numpy as np

from arbs_exchanges.core.domain.entities import Order, OrderType, Symbol
from arbs_exchanges.core.domain.repositories import IOrderRepository

from .bybit_order_link_id_generator import (
    BybitDefaultOrderLinkIdGenerator,
    IOrderLinkIdGenerator,
)


class BybitOrderRepository(IOrderRepository):
    """
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.bybit,
        symbol: Symbol,
        order_link_id_generator: Optional[IOrderLinkIdGenerator] = None,
    ):
        """BybitOrderRepositoryのコンストラクタ

        Args:
            ccxt_exchange (ccxt.Exchange): ccxtのexchange
            symbol (Symbol): 通貨ペア. 通貨ペアの内容によって、requestのparams値が変わるので、依存関係として受け取る
            order_link_id_generator (Optional[IOrderLinkIdGenerator]): order_link_idを生成するインターフェース. Noneの場合は、defaultのOrderLinkIdGeneratorを使用する
        """
        assert isinstance(ccxt_exchange, ccxt.bybit)
        assert symbol in [
            Symbol.BYBIT_LINEAR_BTCUSDT
        ], f"symbol must be BYBIT_LINEAR_BTCUSDT, but {symbol}"

        self._ccxt_exchange = ccxt_exchange
        self._symbol = symbol
        self._order_link_id_generator = (
            order_link_id_generator or BybitDefaultOrderLinkIdGenerator()
        )

        self._logger = getLogger(__class__.__name__)

    @property
    def _category(self) -> str:
        """Bybitのカテゴリを返す. 通貨ペアによって変わる

        Raises:
            ValueError: 通貨ペアが不正な場合

        Returns:
            str: カテゴリ
        """
        if self._symbol == Symbol.BYBIT_LINEAR_BTCUSDT:
            return "linear"
        raise ValueError(f"Invalid symbol: {self._symbol}")

    def _create_order(
        self,
        order_type: OrderType,
        size_with_sign: Decimal,
        price: Decimal = Decimal("nan"),
        post_only: bool = False,
    ) -> Order:
        """注文を作成する

        Args:
            order_type (OrderType): 注文タイプ
            size_with_sign (Decimal): 注文量. 正負の数で指定する.
            price (Decimal): 注文価格
            post_only (bool): post_onlyかどうか. trueの場合、成り行きになる場合は注文が自動的に取り消される

        ccxtから返却されるdictの例. bybitからは orderId しか返ってこない. これが返ってきた場合、無事に注文は成立しているので
        エラーは出さずに返すことにする
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
        assert size_with_sign != 0

        order_link_id = self._order_link_id_generator.generate()
        params = {
            "position_idx": 0,
            "order_link_id": order_link_id,
            "category": self._category,
        }
        if post_only:
            params["timeInForce"] = "PO"

        side = _to_side_str(size_with_sign)
        size = abs(size_with_sign)
        if price.is_nan():
            price = None

        self._logger.info(
            f"create_order(symbol={self._symbol.value}, order_type={order_type.value}, side={side}, amount={size}, price={price})"
        )
        res_dict = self._ccxt_exchange.create_order(
            symbol=self._symbol.value,
            type=order_type.value,
            side=side,
            amount=size,
            price=price,
            params=params,
        )
        if order_type == OrderType.MARKET:
            # market orderの場合、priceは nan で返す
            price = Decimal("nan")

        order = Order(
            order_type=order_type,
            order_id=res_dict["id"],
            symbol=self._symbol,
            size_with_sign=size_with_sign,
            price=price,
        )

        return order

    def create_market_order(
        self,
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
            order_type=OrderType.MARKET,
            size_with_sign=size_with_sign,
            price=Decimal("nan"),
            post_only=False,
        )

    def create_limit_order(
        self,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:
        """指値注文を出す

        Args:
            size_with_sign (Decimal): 注文量. 正負の数で指定する.
            price (Decimal): 注文価格. 指定しない場合は nan を指定する.
            post_only (bool): post_onlyかどうか. 成行注文の場合は常に False

        Returns:
            Order: 注文
        """
        return self._create_order(
            order_type=OrderType.LIMIT,
            size_with_sign=size_with_sign,
            price=price,
            post_only=post_only,
        )

    def remove_order(self, order_id: str) -> Order:
        """注文をキャンセルする

        Args:
            symbol (Symbol): 通貨ペア
            order_id (str): 注文ID

        Returns:
            Order: 注文
        """
        res_dict = self._ccxt_exchange.cancel_order(
            id=order_id,
            symbol=self._symbol.value,
        )
        return Order(
            order_type=OrderType.LIMIT,
            order_id=res_dict["id"],
            symbol=self._symbol,
            # データがないのでnanで返す
            size_with_sign=Decimal("nan"),
            price=Decimal("nan"),
        )

    def remove_all_orders(self):
        """全ての注文をキャンセルする"""
        self._ccxt_exchange.cancel_all_orders(
            symbol=self._symbol.value,
        )
        return True

    def update_order(
        self,
        order_id: str,
        size_with_sign: Optional[Decimal] = None,
        price: Optional[Decimal] = None,
    ) -> Order:
        """注文を編集する

        Args:
            symbol (Symbol): 通貨ペア
            order_id (str): 注文ID
            size_with_sign (Decimal): 注文量. 正負の数で指定する.
            price (Decimal): 注文価格. 変えない場合はnanかNoneで指定する

        Returns:
            Order: 注文
        """
        side = _to_side_str(size_with_sign)
        size = abs(size_with_sign)
        if price.is_nan():
            price = None

        res = self._ccxt_exchange.edit_order(
            id=order_id,
            symbol=self._symbol.value,
            type=OrderType.LIMIT.value,
            side=side,
            amount=size,
            price=price,
            params={"category": self._category},
        )

        return Order(
            order_type=OrderType.LIMIT,
            order_id=res["id"],
            symbol=self._symbol,
            size_with_sign=size_with_sign,
            price=price if price is not None else Decimal("nan"),
        )

    def get_latest_orders(self) -> list[Order]:
        """注文を取得する

        Returns:
            list[Order]: 注文のリスト
        """
        orders = self._ccxt_exchange.fetch_closed_orders(
            symbol=self._symbol.value,
            params={"category": self._category},
        )
        return [
            Order(
                order_type=OrderType.LIMIT,
                order_id=order["id"],
                symbol=self._symbol,
                size_with_sign=(
                    Decimal(order["amount"])
                    if order["amount"] is not None
                    else Decimal("nan")
                ),
                price=(
                    Decimal(order["price"])
                    if order["price"] is not None
                    else Decimal("nan")
                ),
            )
            for order in orders
        ]

    def get_open_orders(self) -> list[Order]:
        """未決済の注文を取得する

        Returns:
            list[Order]: 未決済の注文のリスト
        """
        orders = self._ccxt_exchange.fetch_open_orders(
            symbol=self._symbol.value,
            params={"category": self._category},
        )
        return [
            Order(
                order_type=OrderType.LIMIT,
                order_id=order["id"],
                symbol=self._symbol,
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
