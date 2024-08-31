import math
from logging import getLogger
from typing import Callable, Union

import ccxt

from ..common import CcxtOrderer, CcxtOrdererConfig, bF_Symbol, ccxt_Symbol


class IFeeGetter:
    def taker_fee(self) -> float:
        ...


class BitflyerOrderer(CcxtOrderer):
    """
    - https://github.com/ccxt/ccxt/blob/master/python/ccxt/bitflyer.py
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.bitflyer,
        fee_getter: IFeeGetter,
        symbol: Union[ccxt_Symbol, bF_Symbol],
    ):
        assert isinstance(ccxt_exchange, ccxt.bitflyer)
        # orderer内ではccxtの表現に合わせる.
        # でないと、fetch_ordersが正しく動作しないため
        if symbol == "BTC_JPY":
            symbol = "BTC/JPY"
        elif symbol == "ETH_JPY":
            symbol = "ETH/JPY"

        super().__init__(
            ccxt_exchange=ccxt_exchange,
            config=CcxtOrdererConfig(
                symbol=symbol,
                sizer=_init_sizer(symbol=symbol),
                post_only_str=None,
                min_lot_size=_get_min_lot_size(
                    symbol=symbol,
                ),
            ),
            logger=getLogger(__class__.__name__),
        )
        self._fee_getter = fee_getter

    def post_market_order(self, side_int: int, size: float):
        """
        bFでは現物だと手数料があり、手数料込みの証拠金がないと400エラーが発生する。
        そこで、手数料込の発注量になるように調整してAPIを叩くようにする

        エラーの種類:
        - ccxt.base.errors.ExchangeNotAvailable
          - message: {"status":-200,"error_message":"Insufficient funds","data":null}

        ロジックの詳細:

        手数料考慮後の発注量をsize'とすると、徴収後の発注量がsizeに一致すればいいので
          (i) 買う場合
            size' - (size' * fee) = size
            -> size' = size / (1 - fee)
          (ii) 売る場合
            size + (size * fee) = size'
            -> size' = size * (1 + fee)
          まとめると
            size' + (size' - fee * side_int)
            -> size' = size / (1 - fee * side_int)
        """
        fee = self._fee_getter.taker_fee()
        if side_int == 1:
            size_fee = size / (1 - fee)
        else:
            size_fee = size / (1 + fee)
        # 手数料込にするとmin_lot_sizeを下回る場合は、元のsizeで発注
        # SELL 0.001のときの対策
        if size >= self._config.min_lot_size and size_fee < self._config.min_lot_size:
            size_fee = size
        return super().post_market_order(side_int=side_int, size=size_fee)


def _init_sizer(symbol: ccxt_Symbol) -> Callable[[float], float]:
    if symbol == "BTC/JPY":
        return _spot_btc_sizer
    elif symbol == "ETH/JPY":
        return _spot_eth_sizer
    raise ValueError(f"{symbol=} not supported")


"""
min unit、lot sizeは以下を参照
ref: https://bitflyer.com/ja-jp/faq/4-27
"""


def _spot_btc_sizer(size: float) -> float:
    min_unit = 0.00000001  # 10*(-8)
    floored = math.floor(size / min_unit) * min_unit
    return round(floored, 8)


def _spot_eth_sizer(size: float) -> float:
    min_unit = 0.00000001  # 10*(-8)
    floored = math.floor(size / min_unit) * min_unit
    return round(floored, 8)


def _get_min_lot_size(symbol: str) -> float:
    """
    https://bitflyer.com/ja-jp/faq/4-27
    """
    if "BTC" in symbol:
        return 0.0010
    elif "ETH" in symbol:
        return 0.010
    raise ValueError(f"{symbol=} not yet supported")
