import math
from dataclasses import dataclass
from logging import getLogger

try:
    import MetaTrader5 as MT5
except BaseException:
    MT5 = "dummy"


@dataclass
class _OANDAOrdererConfig:
    symbol: str
    magic: int  # 8桁のEAのユニークID. 自分でつけられる
    spread_max_limit: float  # この値より大きいspreadの場合、取引しない


class OANDAOrderer:
    def __init__(
        self,
        mt5: MT5,
        symbol: str,
        magic: int,
        spread_max_limit: float = 0.006,  # 0.6銭
    ):
        self._mt5 = mt5
        self._config = _OANDAOrdererConfig(
            symbol=symbol,
            magic=int(magic),
            spread_max_limit=float(spread_max_limit),
        )

        self._logger = getLogger(__class__.__name__)

    def post_market_order(self, side_int: int, size: float):
        price, spread = self._fetch_market_price_and_spread(side_int=side_int)

        # spreadが広すぎないかチェック
        if spread > self._config.spread_max_limit:
            self._logger.info(
                "Cancel market order because spread is too large:"
                f" {spread=} > {self._config.spread_max_limit:.4}"
            )
            return

        # 100,000通貨単位 = 1 lot
        lot = _to_lot(size)
        if lot < 0.1:
            self._logger.info(
                f"Cancel market order because lot is too small: {lot=}, {size=}"
            )
            return

        order_type = _to_order_type(side_int)

        # https://www.mql5.com/ja/docs/integration/python_self._mt5/self._mt5ordersend_py
        request = {
            # market
            "action": MT5.TRADE_ACTION_DEAL,
            "symbol": self._config.symbol,
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
            "magic": self._config.magic,
            # 自由なコメント
            "comment": "python script open",
            # 手動でキャンセルするまで注文は残る
            "type_time": MT5.ORDER_TIME_GTC,
            # 部分約定の場合残りはキャンセル
            "type_filling": MT5.ORDER_FILLING_IOC,
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
            self._mt5.TRADE_RETCODE_DONE,
            self._mt5.TRADE_RETCODE_DONE_PARTIAL,
        ):
            self._logger.error(f"発注に失敗しました {order_result=}")
            raise
        self._logger.info(f"OANDAの発注に成功しました: {order_result=}")

        # ccxtのunified orderに合わせる
        if order_type == MT5.ORDER_TYPE_BUY:
            side = "buy"
        elif order_type == MT5.ORDER_TYPE_SELL:
            side = "sell"
        return {
            "id": order_result.deal,
            "amount": order_result.volume,
            "price": order_result.price,
            "side": side,
            # "info": {
            #     "retcode": order_result.retcode,
            #     "deal": order_result.deal,
            #     # "order": order_result.order,
            #     "volume": order_result.volume,
            #     "price": order_result.price,
            #     "bid": order_result.bid,
            #     "ask": order_result.ask,
            #     "comment": order_result.comment,
            #     "request_id": order_result.request_id,
            # },
        }

    def _fetch_market_price_and_spread(self, side_int: int) -> dict:
        tick = self._mt5.symbol_info_tick(self._config.symbol)
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

    def merge_open_orders(self):
        """
        buyとshortの両建てになっているときに、
        相殺して1つ(もしくは0)のポジションにする
        """
        positions = self._fetch_positions()
        if len(positions) <= 1:
            self._logger.debug("Cancel merge_open_orders because num of positions <= 1")
            return

        # 一番最大のvolumeをもっているpositionを選択する
        pos1_i = 0
        max_volume = 0
        for i, position in enumerate(positions):
            if position.volume > max_volume:
                pos1_i = i
                max_volume = position.volume

        # pos1固定で、残りのものとmergeしていく
        pos1 = positions[pos1_i]
        for j, pos2 in enumerate(positions):
            # 符号が同じ場合はmergeできないのでskip. (pos1自身の判定もここで)
            if pos1.type == pos2.type:
                continue
            self._logger.debug(f"{pos1=}, {pos2=}をmergeします")
            request = {
                "action": MT5.TRADE_ACTION_CLOSE_BY,
                "position": pos1.ticket,
                "position_by": pos2.ticket,
            }
            order_result = self._mt5.order_send(request)
            if order_result.retcode not in (
                self._mt5.TRADE_RETCODE_DONE,
                self._mt5.TRADE_RETCODE_DONE_PARTIAL,
            ):
                self._logger.warning(
                    f" (※ここは雑でいいのでraiseはしない) Merge発注に失敗しました {order_result=}"
                )
            else:
                self._logger.info(f"OANDAのMergeに成功しました: {order_result=}")

    def _fetch_positions(self):
        res = self._mt5.positions_get(symbol=self._config.symbol)
        ret = ()
        for trade_position in res:
            if trade_position.magic == self._config.magic:
                ret += (trade_position,)
        return ret


def _to_order_type(side_int: int):
    # https://www.mql5.com/ja/docs/integration/python_metatrader5/mt5ordercalcmargin_py#order_type
    if side_int > 0:
        return MT5.ORDER_TYPE_BUY
    elif side_int < 0:
        return MT5.ORDER_TYPE_SELL
    raise ValueError(f"{side_int=} must not be 0")


def _to_lot(size: int) -> float:
    # 通貨単位をlotに変更する
    # 0.1lotが最小単位なので、0.1単位でfloor
    return math.floor(size / 100_000 * 10) / 10
