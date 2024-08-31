from dataclasses import dataclass

import ccxt
import pybotters


@dataclass
class _Config:
    symbol: str


class PhemexRestPositionGetter:
    """
    - https://github.com/ccxt/ccxt/blob/master/python/ccxt/phemex.py
    - https://docs.ccxt.com/en/latest/manual.html#position-structure
    """

    def __init__(self, ccxt_exchange: ccxt.phemex, symbol: str):
        self._phemex = ccxt_exchange
        self._config = _Config(symbol=symbol)
        self._position_type = _position_type(self._config.symbol)

    def current_position(self) -> int:
        positions = self._phemex.fetch_positions(symbols=[self._config.symbol])
        if len(positions) == 0:
            return 0

        total = 0.0
        for pos in positions:
            base_size = pos["contracts"]
            if base_size is None:
                continue
            side_sign = 1 if pos["side"] == "long" else -1
            total += base_size * side_sign

        total = _cast_size(total, self._config.symbol)
        return self._position_type(total)


@dataclass
class PhemexWsPositionGetterConfig:
    symbol: str


class PhemexWsPositionGetter:
    def __init__(
        self, store: pybotters.PhemexDataStore, config: PhemexWsPositionGetterConfig
    ):

        self._store = store
        self._config = config
        self._position_type = _position_type(config.symbol)

        self._current_position = _position_type(0)

    def current_position(self) -> float or int:
        pos_dict = self._store.position.one(self._config.symbol)

        if pos_dict is None or pos_dict["side"] is None:
            pos = 0.0
        else:
            side_int = 1 if pos_dict["side"] == "Buy" else -1
            size_with_sign = float(pos_dict["size"]) * side_int
            pos = size_with_sign

        pos = _cast_size(pos, self._config.symbol)
        return self._position_type(pos)


def _position_type(symbol: str):
    # linear
    if ":USD" in symbol or "u" in symbol or "s" in symbol:
        return float

    # inverse (USD)
    return int


def _cast_size(size: float, symbol: str):
    # linear or spot
    if symbol in ["uBTCUSD", "BTC/USD:USD"]:
        size /= 1000  # 1枚==0.001BTC
        return float(size)

    # inverse (USD)
    return int(size)
