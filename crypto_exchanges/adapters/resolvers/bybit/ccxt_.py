# %%
import os

import ccxt
from dotenv import load_dotenv

load_dotenv()


def init_ccxt_bybit(default_type: str) -> ccxt.bybit:
    """bybitのccxt exchangeを返す

    Args:
        default_type (str): デフォルトの取引タイプ. future or spot

    Returns:
        ccxt.bybit: bybitのccxt exchange
    """
    return ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
            "options": {"defaultType": default_type},
        }
    )


def init_ccxt_bybit_demo() -> ccxt.bybit:
    """demo tradingを有効にしたbybitのccxt exchangeを返す

    Returns:
        ccxt.bybit: bybitのccxt exchange
    """
    ccxt_bybit = init_ccxt_bybit(default_type="future")
    ccxt_bybit.enable_demo_trading(True)
    return ccxt_bybit
