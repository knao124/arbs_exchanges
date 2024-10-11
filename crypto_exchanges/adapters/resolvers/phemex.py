import os
from typing import Literal

import ccxt
from dotenv import load_dotenv

load_dotenv()


def init_ccxt_phemex(
    mode: Literal["testnet", "real"],
) -> ccxt.phemex:
    """phemexのccxt exchangeを返す

    Args:
        mode (str): モード. testnet or real

    Returns:
        ccxt.phemex: phemexのccxt exchange
    """
    if mode == "testnet":
        ccxt_phemex = ccxt.phemex(
            {
                "apiKey": os.environ["PHEMEX_API_KEY_TESTNET"],
                "secret": os.environ["PHEMEX_SECRET_TESTNET"],
            }
        )
        ccxt_phemex.set_sandbox_mode(True)
        return ccxt_phemex
    elif mode == "real":
        return ccxt.phemex(
            {
                "apiKey": os.environ["PHEMEX_API_KEY"],
                "secret": os.environ["PHEMEX_SECRET"],
            }
        )

    raise ValueError(f"invalid mode: {mode}")
