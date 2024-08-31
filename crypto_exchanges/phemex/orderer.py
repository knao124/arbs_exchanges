from logging import getLogger

import ccxt


class PhemexOrderer:
    """
    - https://github.com/ccxt/ccxt/blob/master/python/ccxt/phemex.py
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(self, ccxt_exchange: ccxt.phemex):
        self._phemex = ccxt_exchange
        self._logger = getLogger(__class__.__name__)

    def post_market_order(self, symbol: str, side_int: int, size: float) -> dict:
        side = _to_side_str(side_int)
        size = _cast_size(size, symbol)
        return self._phemex.create_order(symbol, "market", side, size, params={})

    def post_limit_order(
        self, symbol: str, side_int: int, size: float, price: float
    ) -> dict:
        side = _to_side_str(side_int)
        size = _cast_size(size, symbol)
        res = self._phemex.create_order(
            symbol, "limit", side, size, price, params={"timeInForce": "PostOnly"}
        )
        return res

    def cancel_limit_order(self, symbol: str, order_id: str) -> dict:
        return self._phemex.cancel_order(id=order_id, symbol=symbol)

    def edit_limit_order(
        self,
        symbol: str,
        order_id: str,
        side_int: int,
        size: float,
        price: float,
    ) -> dict:
        res = self.cancel_limit_order(
            symbol=symbol,
            order_id=order_id,
        )
        res = self.post_limit_order(
            symbol=symbol, side_int=side_int, size=size, price=price
        )
        return res

    def get_open_orders(self, symbol: str) -> list:
        return self._phemex.fetch_open_orders(symbol=symbol)


def _cast_size(size: float, symbol: str):
    # linear or spot
    if symbol in ["uBTCUSD", "BTC/USD:USD"]:
        size /= 0.001  # 1枚==0.001BTC
        return int(size)

    # inverse (USD)
    return int(size)


def _to_side_str(side_int: int):
    if side_int > 0:
        return "buy"
    if side_int < 0:
        return "sell"
    raise ValueError
