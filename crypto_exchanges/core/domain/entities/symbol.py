from enum import Enum


class Symbol(Enum):
    BYBIT_LINEAR_BTCUSDT = "BTC/USDT:USDT"
    BITFLYER_CFD_BTCJPY = "BTC/JPY:JPY"
    PHEMEX_LINEAR_BTCUSDT = "BTC/USDT:USDT"
    OANDA_USDJPY = "USDJPY"

    @property
    def is_base_jpy(self) -> bool:
        return self in [Symbol.BITFLYER_CFD_BTCJPY]

    @property
    def is_base_usd(self) -> bool:
        return self in [Symbol.BYBIT_LINEAR_BTCUSDT]

    @classmethod
    def from_exchange_name_and_symbol(
        cls, exchange_name: str, exchange_symbol: str
    ) -> "Symbol":
        if exchange_name == "bybit" and exchange_symbol == "BTCUSDT":
            return Symbol.BYBIT_LINEAR_BTCUSDT
        elif exchange_name == "bitflyer" and exchange_symbol == "FX_BTC_JPY":
            return Symbol.BITFLYER_CFD_BTCJPY
        elif exchange_name == "phemex" and exchange_symbol == "BTCUSDT":
            return Symbol.PHEMEX_LINEAR_BTCUSDT
        elif exchange_name == "oanda" and exchange_symbol == "USDJPY":
            return Symbol.OANDA_USDJPY
        else:
            raise ValueError(f"Invalid exchange symbol: {exchange_symbol}")

    def to_exchange_symbol(self) -> str:
        if self == Symbol.BYBIT_LINEAR_BTCUSDT:
            return "BTCUSDT"
        elif self == Symbol.BITFLYER_CFD_BTCJPY:
            return "FX_BTC_JPY"
        elif self == Symbol.PHEMEX_LINEAR_BTCUSDT:
            return "BTCUSDT"
        elif self == Symbol.OANDA_USDJPY:
            return "USDJPY"
        else:
            raise ValueError(f"Invalid symbol: {self}")
