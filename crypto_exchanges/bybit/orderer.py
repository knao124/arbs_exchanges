import math
from logging import getLogger
from uuid import uuid4

import ccxt

from ..common import CcxtOrderer, CcxtOrdererConfig


class DefaultOrderLinkIdGenerator:
    def generate(self) -> str:
        return str(uuid4())


class ITicker:
    def last_price(self) -> float:
        ...


class USDJPYOrderLinkIdGenerator:
    def __init__(self, usdjpy_ticker: ITicker):
        self._usdjpy_ticker = usdjpy_ticker
        self._logger = getLogger(__class__.__name__)

    # 最新のUSDJPYのレート情報が入ったorder_link_idを生成する
    def generate(self) -> str:
        try:
            return self._generate_raw()
        except BaseException as e:
            self._logger.error(
                f"order_link_idのgeneratorでエラーが発生しました: {e}", exc_info=True
            )
        # エラーが起きたらuuid4を36文字で返す
        return self._generate_uuid4_str()[:36]

    def _generate_raw(self) -> str:
        # order_link_id: 最大36文字. 英数字と記号. 記号は - と _ がsupportされている
        price = self._usdjpy_ticker.last_price()
        uuid_str = self._generate_uuid4_str()

        # uuid4で - が入るので、priceとuuidの区切り文字には _ を使う
        original = f"{price:.3f}_{uuid_str}"

        # .は-にreplaceする
        replaced = original.replace(".", "-")

        # 最大36文字
        return replaced[:36]

    def _generate_uuid4_str(self):
        return str(uuid4())


class IOrderLinkIdGenerator:
    def generate(self) -> str:
        ...


class BybitOrderer(CcxtOrderer):
    """
    - https://github.com/ccxt/ccxt/blob/master/python/ccxt/bitflyer.py
    - https://docs.ccxt.com/en/latest/manual.html#order-structure
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.bybit,
        symbol: str,
        settlement_symbol: str,
        order_link_id_generator: IOrderLinkIdGenerator = DefaultOrderLinkIdGenerator(),
    ):
        assert isinstance(ccxt_exchange, ccxt.bybit)
        super().__init__(
            ccxt_exchange=ccxt_exchange,
            config=CcxtOrdererConfig(
                symbol=symbol,
                sizer=_init_sizer(symbol=symbol),
                post_only_str="PO",
                min_lot_size=_get_min_lot_size(
                    ccxt_exchange=ccxt_exchange,
                    symbol=symbol,
                    settlement_symbol=settlement_symbol,
                ),
            ),
            logger=getLogger(__class__.__name__),
        )

        self._order_link_id_generator = order_link_id_generator

    def post_market_order(self, side_int: int, size: float) -> dict:
        # User customized order ID. A max of 36 characters. A user cannot reuse an orderLinkId, with some exceptions.
        # Combinations of numbers, letters (upper and lower cases), dashes, and underscores are supported.
        # Not required for futures, but required for options.
        params = {"order_link_id": self._order_link_id_generator.generate()}
        return super().post_market_order(side_int=side_int, size=size, params=params)

    def post_limit_order(self, side_int: int, size: float, price: float) -> str:
        params = {"order_link_id": self._order_link_id_generator.generate()}
        return super().post_limit_order(
            side_int=side_int, size=size, price=price, params=params
        )


def _init_sizer(symbol: str) -> callable:
    if symbol in ("BTCUSDT"):
        return _btcusdt_sizer
    elif symbol in ("ETHUSDT"):
        return _ethusdt_sizer

    raise ValueError(f"{symbol=} not supported")


def _btcusdt_sizer(size: float):
    min_unit = 0.001
    return math.floor(size / min_unit) * min_unit


def _ethusdt_sizer(size: float):
    min_unit = 0.01
    return math.floor(size / min_unit) * min_unit


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
    # ccxt_exchange.load_markets()
    # base = "BTC"
    # _, quote = symbol.split(base)

    # market = ccxt_exchange.markets[f"{base}/{quote}:{settlement_symbol}"]
    # return market["limits"]["amount"]["min"]
