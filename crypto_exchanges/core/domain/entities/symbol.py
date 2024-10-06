from enum import Enum


class Symbol(Enum):
    BYBIT_LINEAR_BTCUSDT = "BTC/USDT:USDT"
    BITFLYER_CFD_BTCJPY = "BTC/JPY:JPY"

    @property
    def is_base_jpy(self) -> bool:
        return self in [Symbol.BITFLYER_CFD_BTCJPY]

    @property
    def is_base_usd(self) -> bool:
        return self in [Symbol.BYBIT_LINEAR_BTCUSDT]
