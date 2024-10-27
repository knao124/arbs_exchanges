import math
from dataclasses import dataclass
from decimal import Decimal
from logging import getLogger
import numpy as np

from arbs_exchanges.core.domain.entities import Order, Symbol
from arbs_exchanges.core.domain.repositories import (
    IOrderRepository,
    IPositionRepository,
)

from .mt5_interface import MetaTrader5Interface


@dataclass
class MT5Const:
    TRADE_ACTION_DEAL: int
    TRADE_ACTION_CLOSE_BY: int
    ORDER_TIME_GTC: int
    ORDER_FILLING_IOC: int
    ORDER_TYPE_BUY: int
    ORDER_TYPE_SELL: int
    TRADE_RETCODE_DONE: int
    TRADE_RETCODE_DONE_PARTIAL: int


def get_mt5_const() -> MT5Const:
    try:
        import MetaTrader5 as MT5

        return MT5Const(
            TRADE_ACTION_DEAL=MT5.TRADE_ACTION_DEAL,
            TRADE_ACTION_CLOSE_BY=MT5.TRADE_ACTION_CLOSE_BY,
            ORDER_TIME_GTC=MT5.ORDER_TIME_GTC,
            ORDER_FILLING_IOC=MT5.ORDER_FILLING_IOC,
            ORDER_TYPE_BUY=MT5.ORDER_TYPE_BUY,
            ORDER_TYPE_SELL=MT5.ORDER_TYPE_SELL,
            TRADE_RETCODE_DONE=MT5.TRADE_RETCODE_DONE,
            TRADE_RETCODE_DONE_PARTIAL=MT5.TRADE_RETCODE_DONE_PARTIAL,
        )
    except ImportError:
        # Mac用. 2024-10-19 時点の値
        return MT5Const(
            TRADE_ACTION_DEAL=1,
            TRADE_ACTION_CLOSE_BY=10,
            ORDER_TIME_GTC=0,
            ORDER_FILLING_IOC=1,
            ORDER_TYPE_BUY=0,
            ORDER_TYPE_SELL=1,
            TRADE_RETCODE_DONE=10009,
            TRADE_RETCODE_DONE_PARTIAL=10010,
        )


class OandaOrderRepository(IOrderRepository):
    def __init__(
        self,
        mt5: MetaTrader5Interface,
        position_repo: IPositionRepository,
        symbol: Symbol,
        magic: int,
        spread_max_limit: float = 0.006,  # 0.6銭
    ):
        """Oandaの発注を行う

        Args:
            mt5 (MetaTrader5Interface): MetaTrader5のインターフェース
            position_repo (IPositionRepository): ポジションのリポジトリ
            symbol (Symbol): 通貨ペア
            magic (int): 8桁のEAのユニークID. 自分でつけられる
            spread_max_limit (float, optional): この値より大きいspreadの場合、取引しない. Defaults to 0.006.
        """
        self._mt5 = mt5
        self._position_repo = position_repo
        self._symbol = symbol
        self._magic = magic
        self._spread_max_limit = spread_max_limit
        self._mt5_const = get_mt5_const()

        self._logger = getLogger(__class__.__name__)

    def create_market_order(self, size_with_sign: Decimal) -> Order:
        price, spread = self._fetch_market_price_and_spread(
            side_int=np.sign(size_with_sign)
        )

        # spreadが広すぎないかチェック
        if spread > self._spread_max_limit:
            self._logger.info(
                "Cancel market order because spread is too large:"
                f" {spread=} > {self._spread_max_limit:.4}"
            )
            raise ValueError("spread is too large")

        # 100,000通貨単位 = 1 lot
        lot = _to_lot(size_with_sign)
        if lot < 0.1:
            self._logger.info(
                f"Cancel market order because lot is too small: {lot=}, {size_with_sign=}"
            )
            raise ValueError("lot is too small")

        order_type = _to_order_type(size_with_sign, self._mt5_const)

        # https://www.mql5.com/ja/docs/constants/structures/mqltraderequest
        request = {
            # market
            "action": self._mt5_const.TRADE_ACTION_DEAL,
            "symbol": self._symbol.value,
            # buyかsellか
            "type": order_type,
            "volume": lot,
            "price": price,
            # この2つは0.0で良いらしい
            # "sl": 0.1,
            # "tp": 0.1,
            # 最大許容slippageのpips?
            "deviation": 10,
            # clientIdっぽいもの
            "magic": self._magic,
            # 自由なコメント
            "comment": "python script open",
            # 手動でキャンセルするまで注文は残る
            "type_time": self._mt5_const.ORDER_TIME_GTC,
            # 部分約定の場合残りはキャンセル
            "type_filling": self._mt5_const.ORDER_FILLING_IOC,
        }

        self._logger.debug("  OANDAで発注します")
        self._logger.debug(f"    {request=}")

        order_check_result = self._mt5.order_check(request)
        self._logger.debug(f"    {order_check_result=}")

        # https://www.mql5.com/ja/docs/constants/structures/mqltraderesult
        order_result = self._mt5.order_send(request)

        # 400系のerrorの場合、order_resultがNoneなので先にlast_errorのチェックを実施
        # - last_error: https://www.mql5.com/ja/docs/integration/python_metatrader5/mt5lasterror_py
        error_code, error_message = self._mt5.last_error()
        if error_code != 1:
            self._logger.error(f"{error_code=}, {error_message=}, {request=}")
            raise
        if order_result is None:
            self._logger.error(f"想定外のエラー {request=}")
            raise
        if order_result.retcode not in (
            self._mt5_const.TRADE_RETCODE_DONE,
            self._mt5_const.TRADE_RETCODE_DONE_PARTIAL,
        ):
            self._logger.error(f"発注に失敗しました {order_result=}")
            raise
        self._logger.info(f"OANDAの発注に成功しました: {order_result=}")

        # ccxtのunified orderに合わせる
        if order_type == self._mt5_const.ORDER_TYPE_BUY:
            side_int = 1
        elif order_type == self._mt5_const.ORDER_TYPE_SELL:
            side_int = -1
        return Order(
            order_type=order_type,
            order_id=order_result.order,
            symbol=self._symbol,
            size_with_sign=order_result.volume * side_int,
            price=order_result.price,
        )

    def _fetch_market_price_and_spread(self, side_int: int) -> tuple[float, float]:
        tick = self._mt5.symbol_info_tick(self._symbol.value)
        ask = tick.ask
        bid = tick.bid
        spread = ask - bid

        if side_int > 0:
            price = ask  # 売り板に当てる
        elif side_int < 0:
            price = bid  # 買い板に当てる
        else:
            raise ValueError(f"{side_int=} must not be 0")

        price = round(price, 4)
        spread = round(spread, 10)

        return price, spread

    def merge_position(self, id1: str, id2: str):
        """
        2つのポジションをマージする
        """
        request = {
            "action": self._mt5_const.TRADE_ACTION_CLOSE_BY,
            "position": id1,
            "position_by": id2,
        }

        order_result = self._mt5.order_send(request)
        if order_result.retcode not in (
            self._mt5_const.TRADE_RETCODE_DONE,
            self._mt5_const.TRADE_RETCODE_DONE_PARTIAL,
        ):
            self._logger.warning(
                f" (※ここは雑でいいのでraiseはしない) Merge発注に失敗しました {order_result=}"
            )
        else:
            self._logger.info(f"OANDAのMergeに成功しました: {order_result=}")

    def merge_positions(self):
        """
        buyとshortの両建てになっているときに、
        相殺して1つ(もしくは0)のポジションにする
        """
        positions = self._position_repo.fetch_positions(self._symbol.value)
        if len(positions) <= 1:
            self._logger.debug("Cancel merge_open_orders because num of positions <= 1")
            return

        # 一番最大のvolumeをもっているpositionを選択する
        pos1_i = 0
        max_volume = 0
        for i, position in enumerate(positions):
            if abs(position.size_with_sign) > max_volume:
                pos1_i = i
                max_volume = abs(position.size_with_sign)
        pos1 = positions[pos1_i]
        positions = [pos for i, pos in enumerate(positions) if i != pos1_i]

        # pos1固定で、残りのものとmergeしていく
        for _, pos2 in enumerate(positions):
            # 符号が同じ場合はmergeできないのでskip.
            if pos1.size_with_sign * pos2.size_with_sign > 0:
                continue
            self.merge_position(id1=pos1.id, id2=pos2.id)

    def create_limit_order(
        self,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:
        raise NotImplementedError("OANDAでは使わない")

    def update_order(
        self,
        order_id: str,
        size_with_sign: Decimal,
        price: Decimal,
    ) -> Order:
        raise NotImplementedError("OANDAでは使わない")

    def remove_order(
        self,
        order_id: str,
    ) -> Order:
        raise NotImplementedError("OANDAでは使わない")

    def remove_all_orders(
        self,
    ) -> bool:
        raise NotImplementedError("OANDAでは使わない")

    def get_open_orders(
        self,
    ) -> list[Order]:
        raise NotImplementedError("OANDAでは使わない")

    def get_latest_orders(
        self,
    ) -> list[Order]:
        raise NotImplementedError("OANDAでは使わない")


def _to_order_type(side_int: int, const: MT5Const):
    # https://www.mql5.com/ja/docs/integration/python_metatrader5/mt5ordercalcmargin_py#order_type
    if side_int > 0:
        return const.ORDER_TYPE_BUY
    elif side_int < 0:
        return const.ORDER_TYPE_SELL
    raise ValueError(f"{side_int=} must not be 0")


def _to_lot(size_with_sign: Decimal) -> float:
    # 通貨単位をlotに変更する
    # 0.1lotが最小単位なので、0.1単位でfloor
    return math.floor(size_with_sign / 100_000 * 10) / 10
