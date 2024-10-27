# %%
from decimal import Decimal
from logging import getLogger

import ccxt

from arbs_exchanges.core.domain.entities import Order, OrderType, Symbol
from arbs_exchanges.core.domain.repositories import IOrderRepository


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
        amount = str(abs(size_with_sign))

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
        amount = str(abs(size_with_sign))
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
        amount = str(abs(size_with_sign))
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
        open_orders = self.get_open_orders()
        for open_order in open_orders:
            self.remove_order(open_order.order_id)
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
                order_type=res_dict["type"],
                order_id=res_dict["id"],
                symbol=self._symbol,
                size_with_sign=Decimal(str(res_dict["amount"])),
                price=Decimal(str(res_dict["price"])),
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
        # {
        #     "id": "JRF20230627-141102-185412",
        #     "clientOrderId": None,
        #     "info": {
        #         "id": "2808714344",
        #         "child_order_id": "JFX20230627-141102-623226F",
        #         "product_code": "FX_BTC_JPY",
        #         "side": "BUY",
        #         "child_order_type": "LIMIT",
        #         "price": "4515083.000000000000",
        #         "average_price": "4515083.000000000000",
        #         "size": "0.989100000000",
        #         "child_order_state": "COMPLETED",
        #         "expire_date": "2023-07-27T14:11:02",
        #         "child_order_date": "2023-06-27T14:11:02",
        #         "child_order_acceptance_id": "JRF20230627-141102-185412",
        #         "outstanding_size": "0.000000000000",
        #         "cancel_size": "0.000000000000",
        #         "executed_size": "0.989100000000",
        #         "total_commission": "0.000000000000",
        #         "time_in_force": "GTC",
        #     },
        #     "timestamp": 1687875062000,
        #     "datetime": "2023-06-27T14:11:02.000Z",
        #     "lastTradeTimestamp": None,
        #     "status": "closed",
        #     "symbol": "BTC/JPY:JPY",
        #     "type": "limit",
        #     "timeInForce": None,
        #     "postOnly": None,
        #     "side": "buy",
        #     "price": 4515083.0,
        #     "stopPrice": None,
        #     "triggerPrice": None,
        #     "cost": 4465868.5953,
        #     "amount": 0.9891,
        #     "filled": 0.9891,
        #     "remaining": 0.0,
        #     "fee": {"cost": 0.0, "currency": None, "rate": None},
        #     "average": None,
        #     "trades": [],
        #     "fees": [{"cost": 0.0, "currency": None, "rate": None}],
        #     "lastUpdateTimestamp": None,
        #     "reduceOnly": None,
        #     "takeProfitPrice": None,
        #     "stopLossPrice": None,
        # }
        # {
        #     "id": "JRF20230627-141020-992914",
        #     "clientOrderId": None,
        #     "info": {
        #         "id": "2808715940",
        #         "child_order_id": "JFX20230627-141233-678100F",
        #         "product_code": "FX_BTC_JPY",
        #         "side": "SELL",
        #         "child_order_type": "MARKET",
        #         "price": "0.000000000000",
        #         "average_price": "4492117.000000000000",
        #         "size": "1.978200000000",
        #         "child_order_state": "COMPLETED",
        #         "expire_date": "2023-07-27T14:10:20",
        #         "child_order_date": "2023-06-27T14:12:32",
        #         "child_order_acceptance_id": "JRF20230627-141020-992914",
        #         "outstanding_size": "0.000000000000",
        #         "cancel_size": "0.000000000000",
        #         "executed_size": "1.978200000000",
        #         "total_commission": "0.000000000000",
        #         "time_in_force": "GTC",
        #     },
        #     "timestamp": 1687875152000,
        #     "datetime": "2023-06-27T14:12:32.000Z",
        #     "lastTradeTimestamp": None,
        #     "status": "closed",
        #     "symbol": "BTC/JPY:JPY",
        #     "type": "market",
        #     "timeInForce": "IOC",
        #     "postOnly": None,
        #     "side": "sell",
        #     "price": None,
        #     "stopPrice": None,
        #     "triggerPrice": None,
        #     "cost": None,
        #     "amount": 1.9782,
        #     "filled": 1.9782,
        #     "remaining": 0.0,
        #     "fee": {"cost": 0.0, "currency": None, "rate": None},
        #     "average": None,
        #     "trades": [],
        #     "fees": [{"cost": 0.0, "currency": None, "rate": None}],
        #     "lastUpdateTimestamp": None,
        #     "reduceOnly": None,
        #     "takeProfitPrice": None,
        #     "stopLossPrice": None,
        # }
        orders = []
        for res_dict in res_dicts:
            orders.append(
                Order(
                    order_type=res_dict["type"],
                    order_id=res_dict["id"],
                    symbol=self._symbol,
                    size_with_sign=Decimal(str(res_dict["amount"])),
                    price=Decimal(str(res_dict["info"]["average_price"])),
                )
            )
        return orders
