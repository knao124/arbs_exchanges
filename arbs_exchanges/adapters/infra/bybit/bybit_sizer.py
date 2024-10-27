import math


def init_sizer(symbol: str) -> callable:
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
