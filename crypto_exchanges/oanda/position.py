from dataclasses import dataclass

import numpy as np

try:
    import MetaTrader5 as MT5
except BaseException:
    MT5 = "dummy"


@dataclass
class OANDAPositionConfig:
    symbol: str
    magic: int


class OANDAPosition:
    def __init__(self, mt5: MT5, config: OANDAPositionConfig):
        self._mt5 = mt5
        self._config = config

    def current_position(self):
        total = 0
        positions = self.fetch_position()
        for pos in positions:
            size = _to_currency(pos.volume)
            if pos.type == MT5.ORDER_TYPE_BUY:
                sign = 1
            elif pos.type == MT5.ORDER_TYPE_SELL:
                sign = -1
            else:
                continue
            total += sign * size
        return total

    def avg_price(self) -> float:
        positions = self.fetch_position()
        if len(positions) == 0:
            return np.nan

        # price_openの加重平均を返す
        total_size = 0
        total_value = 0
        for pos in positions:
            size = _to_currency(pos.volume)
            if pos.type == MT5.ORDER_TYPE_BUY:
                sign = 1
            elif pos.type == MT5.ORDER_TYPE_SELL:
                sign = -1
            else:
                continue
            total_value += pos.price_open * sign * size
            total_size += sign * size
        return total_value / total_size

    def fetch_position(self):
        # https://www.mql5.com/ja/docs/integration/python_metatrader5/mt5positionsget_py
        # TradePosition(
        #     ticket=4098461,
        #     time=1667386683,
        #     time_msc=1667386683719,
        #     time_update=1667386683,
        #     time_update_msc=1667386683719,
        #     type=1,
        #     magic=12345678,
        #     identifier=4098461,
        #     reason=3,
        #     volume=0.2,
        #     price_open=147.321,
        #     sl=0.0,
        #     tp=0.0,
        #     price_current=147.721,
        #     swap=-350.0,
        #     profit=-8000.0,
        #     symbol="USDJPY",
        #     comment="python script op",
        #     external_id="",
        # )
        res = self._mt5.positions_get(symbol=self._config.symbol)
        positions = ()
        for trade_position in res:
            if trade_position.magic == self._config.magic:
                positions += (trade_position,)
        return positions


def _to_currency(volume: float):
    return int(100_000 * volume)


class DummyPosition:
    def current_position(self):
        return 0.0

    def avg_price(self):
        return 0.0
