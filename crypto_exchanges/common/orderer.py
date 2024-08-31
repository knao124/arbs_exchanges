from dataclasses import dataclass
from logging import Logger, getLogger
from typing import Callable

import ccxt


@dataclass
class CcxtOrdererConfig:
    symbol: str
    sizer: Callable
    post_only_str: str
    min_lot_size: float


class CcxtOrderer:
    """
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.Exchange,
        config: CcxtOrdererConfig,
        logger: Logger,
    ):
        self._ccxt_exchange = ccxt_exchange
        self._config = config

        if logger is None:
            logger = getLogger(__class__.__name__)

        self._logger = logger

    def post_market_order(
        self,
        side_int: int,
        size: float,
        params: dict = {},
    ) -> dict:
        side = _to_side_str(side_int)
        size = self._config.sizer(size)
        default_params = {"position_idx": 0}
        params = dict(default_params, **params)

        self._logger.debug(f"post_market_order({side}, {size}), {self._config.sizer=}")
        if size < self._config.min_lot_size:
            self._logger.debug(f"skip because {size=} < {self._config.min_lot_size=}")
            return
        return self._ccxt_exchange.create_order(
            self._config.symbol,
            "market",
            side,
            size,
            params=params,
        )

    def post_limit_order(
        self,
        side_int: int,
        size: float,
        price: float,
        post_only: bool = True,
        params: dict = {},
    ) -> dict:
        side = _to_side_str(side_int)
        size = self._config.sizer(size)
        default_params = {"position_idx": 0}
        params = dict(default_params, **params)

        if post_only:
            params["timeInForce"] = self._config.post_only_str

        if size < self._config.min_lot_size:
            self._logger.debug(f"skip because {size=} < {self._config.min_lot_size=}")
            return

        self._logger.debug(f"post_limit_order({side=}, {size=}, {price=}, {params=})")
        return self._ccxt_exchange.create_order(
            self._config.symbol,
            "limit",
            side,
            size,
            price,
            params=params,
        )

    def cancel_limit_order(self, order_id: str) -> dict:
        return self._ccxt_exchange.cancel_order(id=order_id, symbol=self._config.symbol)

    def edit_limit_order(
        self, order_id: str, side_int: int, size: float, price: float, params: dict = {}
    ) -> dict:
        side = _to_side_str(side_int)
        size = self._config.sizer(size)
        return self._ccxt_exchange.edit_order(
            id=order_id,
            symbol=self._config.symbol,
            type="limit",
            side=side,
            amount=size,
            price=price,
            params=params,
        )

    def get_latest_orders(self) -> list:
        return self._ccxt_exchange.fetch_orders(symbol=self._config.symbol)

    def get_open_orders(self) -> list:
        return self._ccxt_exchange.fetch_open_orders(symbol=self._config.symbol)

    def cancel_all_orders(self):
        orders = self.get_open_orders()
        for order in orders:
            self.cancel_limit_order(order_id=order["id"])


def _to_side_str(side_int: int):
    if side_int > 0:
        return "buy"
    if side_int < 0:
        return "sell"
    raise ValueError
