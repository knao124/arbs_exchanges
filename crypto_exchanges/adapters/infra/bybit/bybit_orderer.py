import math

import ccxt

from crypto_exchanges.core.use_cases.interfaces import IOrderer, IOrderLinkIdGenerator
from crypto_exchanges.core.use_cases.order_link_id_generator import (
    DefaultOrderLinkIdGenerator,
)


class BybitOrderer(IOrderer):
    """
    - https://github.com/ccxt/ccxt/blob/master/python/ccxt/bitflyer.py
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(
        self,
        ccxt_orderer: IOrderer,
        order_link_id_generator: IOrderLinkIdGenerator = DefaultOrderLinkIdGenerator(),
    ):
        self._ccxt_orderer = ccxt_orderer
        self._order_link_id_generator = order_link_id_generator

    def post_market_order(self, side_int: int, size: float) -> dict:
        # User customized order ID. A max of 36 characters. A user cannot reuse an orderLinkId, with some exceptions.
        # Combinations of numbers, letters (upper and lower cases), dashes, and underscores are supported.
        # Not required for futures, but required for options.
        """
        返却されるdictの例

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
        """
        params = {
            "order_link_id": self._order_link_id_generator.generate(),
        }
        return self._ccxt_orderer.post_market_order(
            side_int=side_int,
            size=size,
            params=params,
        )

    def post_limit_order(
        self,
        side_int: int,
        size: float,
        price: float,
        post_only: bool = False,
        params: dict = {},
    ) -> dict:
        params["order_link_id"] = self._order_link_id_generator.generate()
        return self._ccxt_orderer.post_limit_order(
            side_int=side_int,
            size=size,
            price=price,
            post_only=post_only,
            params=params,
        )

    def cancel_limit_order(self, order_id: str) -> dict:
        return self._ccxt_orderer.cancel_limit_order(order_id)

    def edit_limit_order(
        self, order_id: str, side_int: int, size: float, price: float, params: dict = {}
    ) -> dict:
        return self._ccxt_orderer.edit_limit_order(
            order_id=order_id,
            side_int=side_int,
            size=size,
            price=price,
            params=params,
        )

    def fetch_latest_orders(self) -> list:
        return self._ccxt_orderer.fetch_latest_orders()

    def fetch_open_orders(self) -> list:
        return self._ccxt_orderer.fetch_open_orders()

    def cancel_all_orders(self) -> None:
        return self._ccxt_orderer.cancel_all_orders()


def _get_min_lot_size(ccxt_exchange: ccxt.bybit, symbol: str, settlement_symbol):
    """
    BTCUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=BTCUSDT
    ETHUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=ETHUSDT
    """
    if "BTCUSDT" in symbol:
        return 0.0010
    elif "ETHUSDT" in symbol:
        return 0.010
    raise ValueError(f"今は対応していないけどいずれ対応しないといけない: {symbol=}")
