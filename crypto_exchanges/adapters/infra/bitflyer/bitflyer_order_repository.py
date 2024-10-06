# %%
from decimal import Decimal
from logging import getLogger

import ccxt

from crypto_exchanges.core.domain.entities import Order, OrderType, Symbol
from crypto_exchanges.core.domain.repositories import IOrderRepository


def _to_side_str(size_with_sign: Decimal) -> str:
    if size_with_sign > 0:
        return "buy"
    elif size_with_sign < 0:
        return "sell"
    raise ValueError("size_with_sign must be positive or negative")


class BitflyerOrderRepository(IOrderRepository):
    def __init__(
        self,
        ccxt_exchange: ccxt.bitflyer,
        symbol: Symbol,
    ):
        assert isinstance(ccxt_exchange, ccxt.bitflyer)
        assert symbol in [Symbol.BITFLYER_CFD_BTCJPY]

        self._ccxt_exchange = ccxt_exchange
        self._symbol = symbol

        self._logger = getLogger(__name__)

    def create_market_order(
        self,
        size_with_sign: Decimal,
    ) -> Order:

        symbol = self._symbol.value
        side = _to_side_str(size_with_sign)
        amount = abs(size_with_sign)

        self._logger.info(
            f"create_market_order(symbol={symbol}, side={side}, amount={amount})"
        )
        res_dict = self._ccxt_exchange.create_market_order(
            symbol=symbol,
            side=side,
            amount=amount,
        )

        return Order(
            order_type=OrderType.MARKET,
            order_id=res_dict["id"],
            symbol=self._symbol,
            size_with_sign=size_with_sign,
            price=Decimal("nan"),
        )

    def create_limit_order(
        self,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:

        assert post_only is False, "bitflyer は post_only の指値注文はできない"

        symbol = self._symbol.value
        side = _to_side_str(size_with_sign)
        amount = abs(size_with_sign)
        price = int(price)

        self._logger.info(
            f"create_limit_order(symbol={symbol}, side={side}, amount={amount}, price={price})"
        )
        res_dict = self._ccxt_exchange.create_limit_order(
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
        )

        return Order(
            order_type=OrderType.LIMIT,
            order_id=res_dict["id"],
            symbol=self._symbol,
            size_with_sign=size_with_sign,
            price=price,
        )

    def update_order(
        self,
        order_id: str,
        size_with_sign: Decimal,
        price: Decimal,
    ) -> Order:

        symbol = self._symbol.value
        side = _to_side_str(size_with_sign)
        amount = abs(size_with_sign)
        price = int(price)
        order_type = OrderType.LIMIT.value

        self._logger.info(
            f"update_order(id={order_id}, symbol={symbol}, type={order_type}, side={side}, amount={amount}, price={price})"
        )
        res_dict = self._ccxt_exchange.edit_order(
            id=order_id,
            symbol=symbol,
            type=order_type,
            side=side,
            amount=amount,
            price=price,
        )

        return Order(
            order_type=OrderType.LIMIT,
            order_id=res_dict["id"],
            symbol=self._symbol,
            size_with_sign=size_with_sign,
            price=price,
        )

    def remove_order(
        self,
        order_id: str,
    ) -> Order:

        symbol = self._symbol.value
        self._logger.info(f"remove_order(id={order_id}, symbol={symbol})")
        res_dict = self._ccxt_exchange.cancel_order(
            id=order_id,
            symbol=symbol,
        )

        return Order(
            order_type=OrderType.LIMIT,
            order_id=res_dict["id"],
            symbol=self._symbol,
            size_with_sign=Decimal("nan"),
            price=Decimal("nan"),
        )

    def remove_all_orders(
        self,
    ) -> bool:
        symbol = self._symbol.value
        self._logger.info(f"remove_all_orders(symbol={symbol})")
        _ = self._ccxt_exchange.cancel_all_orders(
            symbol=symbol,
        )
        return True

    def get_open_orders(
        self,
    ) -> list[Order]:
        symbol = self._symbol.value
        self._logger.info(f"get_open_orders(symbol={symbol})")
        res_dicts = self._ccxt_exchange.fetch_open_orders(
            symbol=symbol,
        )
        return [
            Order(
                order_type=OrderType.LIMIT,
                order_id=res_dict["id"],
                symbol=self._symbol,
                size_with_sign=Decimal(res_dict["amount"]),
                price=Decimal(res_dict["price"]),
            )
            for res_dict in res_dicts
        ]

    def get_latest_orders(
        self,
    ) -> list[Order]:
        symbol = self._symbol.value
        self._logger.info(f"get_latest_orders(symbol={symbol})")
        res_dicts = self._ccxt_exchange.fetch_closed_orders(
            symbol=symbol,
        )
        return [
            Order(
                # TODO: 注文タイプをどうやって取得するか
                order_type=res_dict["order_type"],
                order_id=res_dict["id"],
                symbol=self._symbol,
                size_with_sign=Decimal(res_dict["amount"]),
                price=Decimal(res_dict["price"]),
            )
            for res_dict in res_dicts
        ]
