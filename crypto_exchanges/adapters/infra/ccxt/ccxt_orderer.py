from dataclasses import dataclass
from decimal import Decimal
from logging import getLogger
from typing import Optional

import ccxt

from crypto_exchanges.adapters.interfaces import ISizer
from crypto_exchanges.core.use_cases.interfaces import IOrderer


@dataclass
class _CcxtOrdererConfig:
    symbol: str
    sizer: ISizer
    post_only_str: Optional[str]
    min_lot_size: Decimal


class CcxtOrderer(IOrderer):
    """
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.Exchange,
        sizer: ISizer,
        symbol: str,
        post_only_str: str,
        min_lot_size: Decimal,
    ):
        """CcxtOrdererのコンストラクタ

        Args:
            ccxt_exchange (ccxt.Exchange): ccxtのexchange
            sizer (ISizer): 注文量を調整する関数
            symbol (str): 通貨ペア
            post_only_str (str): post_onlyの文字列
            min_lot_size (Decimal): 最小注文量
        """
        self._ccxt_exchange = ccxt_exchange
        self._config = _CcxtOrdererConfig(
            symbol=symbol,
            sizer=sizer,
            post_only_str=post_only_str,
            min_lot_size=min_lot_size,
        )
        self._logger = getLogger(__class__.__name__)

    def post_market_order(
        self,
        side_int: int,
        size: float,
        params: dict = {},
    ) -> dict:
        """成行注文を出す

        Args:
            side_int (int): 売買方向. -1: 売り, 1: 買い
            size (float): 注文量. 正の数で指定する.
            params (dict, optional): オプション引数. Defaults to {}.

        Returns:
            dict: 注文結果
        """
        side = _to_side_str(side_int)
        size = self._config.sizer(size)
        assert size > 0, f"size must be positive, but {size=}"

        default_params = {"position_idx": 0}
        params = dict(default_params, **params)

        if size < self._config.min_lot_size:
            self._logger.debug(
                f"skip post_marke_order({side}, {size}) because {size=} < {self._config.min_lot_size=}"
            )
            return {}
        self._logger.debug(f"post_market_order({side}, {size})")
        return self._ccxt_exchange.create_order(
            symbol=self._config.symbol,
            type="market",
            side=side,
            amount=size,
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
        """指値注文を出す

        Args:
            side_int (int): 売買方向
            size (float): 注文量
            price (float): 注文価格
            params (dict, optional): オプション引数. Defaults to {}.

        Returns:
            dict: 注文結果

        Raises:
            ValueError: post_only_strがNoneの場合
        """
        side = _to_side_str(side_int)
        size = self._config.sizer(size)
        default_params = {"position_idx": 0}
        params = dict(default_params, **params)

        assert size > 0, f"size must be positive, but {size=}"
        if post_only:
            s = self._config.post_only_str
            assert s is not None, "config post_only_str is None"
            params["timeInForce"] = s

        if size < self._config.min_lot_size:
            self._logger.debug(f"skip because {size=} < {self._config.min_lot_size=}")
            return {}

        self._logger.debug(f"post_limit_order({side=}, {size=}, {price=}, {params=})")
        return self._ccxt_exchange.create_order(
            symbol=self._config.symbol,
            type="limit",
            side=side,
            amount=size,
            price=price,
            params=params,
        )

    def cancel_limit_order(self, order_id: str) -> dict:
        """注文をキャンセルする

        Args:
            order_id (str): 注文ID

        Returns:
            dict: 注文結果
        """
        return self._ccxt_exchange.cancel_order(id=order_id, symbol=self._config.symbol)

    def edit_limit_order(
        self, order_id: str, side_int: int, size: float, price: float, params: dict = {}
    ) -> dict:
        """注文を編集する

        Args:
            order_id (str): 注文ID
            side_int (int): 売買方向
            size (float): 注文量
            price (float): 注文価格
            params (dict, optional): オプション引数. Defaults to {}.

        Returns:
            dict: 注文結果
        """
        side = _to_side_str(side_int)
        size = self._config.sizer(size)
        assert size > 0, f"size must be positive, but {size=}"
        self._logger.debug(
            f"edit_limit_order({order_id=}, {side=}, {size=}, {price=}, {params=})"
        )
        return self._ccxt_exchange.edit_order(
            id=order_id,
            symbol=self._config.symbol,
            type="limit",
            side=side,
            amount=size,
            price=price,
            params=params,
        )

    def fetch_latest_orders(self) -> list:
        """注文を取得する

        Returns:
            list: 注文のリスト
        """
        return self._ccxt_exchange.fetch_orders(symbol=self._config.symbol)

    def fetch_open_orders(self) -> list:
        """未決済の注文を取得する

        Returns:
            list: 未決済の注文のリスト
        """
        return self._ccxt_exchange.fetch_open_orders(symbol=self._config.symbol)

    def cancel_all_orders(self):
        """未決済の注文をキャンセルする"""
        orders = self.fetch_open_orders()
        for order in orders:
            self.cancel_limit_order(order_id=order["id"])


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
