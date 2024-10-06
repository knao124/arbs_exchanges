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

    @classmethod
    def from_exchange_symbol(cls, exchange_symbol: str) -> "Symbol":
        if exchange_symbol == "BTCUSDT":
            return Symbol.BYBIT_LINEAR_BTCUSDT
        elif exchange_symbol == "FX_BTC_JPY":
            return Symbol.BITFLYER_CFD_BTCJPY
        else:
            raise ValueError(f"Invalid exchange symbol: {exchange_symbol}")

    def to_exchange_symbol(self) -> str:
        if self == Symbol.BYBIT_LINEAR_BTCUSDT:
            return "BTCUSDT"
        elif self == Symbol.BITFLYER_CFD_BTCJPY:
            return "FX_BTC_JPY"
        else:
            raise ValueError(f"Invalid symbol: {self}")
