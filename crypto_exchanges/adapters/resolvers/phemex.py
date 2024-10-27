import os
from typing import Literal

import ccxt
from dotenv import load_dotenv

from arbs_exchanges.core.domain.entities import Symbol

load_dotenv()


def init_ccxt_phemex(
    mode: Literal["testnet", "real"],
    position_mode: Literal["one_way", "hedged"] = "one_way",
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
        if position_mode == "one_way":
            set_position_mode_one_way(ccxt_phemex)
        return ccxt_phemex
    elif mode == "real":
        return ccxt.phemex(
            {
                "apiKey": os.environ["PHEMEX_API_KEY"],
                "secret": os.environ["PHEMEX_SECRET"],
            }
        )

    raise ValueError(f"invalid mode: {mode}")


def set_position_mode_one_way(
    ccxt_phemex: ccxt.phemex,
):
    symbols = [Symbol.PHEMEX_LINEAR_BTCUSDT]
    for symbol in symbols:
        ccxt_phemex.set_position_mode(
            hedged=False,
            symbol=symbol.value,
        )


PHEMEX_TESTNET_WS_URL = "wss://testnet-api.phemex.com/ws"
PHEMEX_REAL_WS_URL = "wss://api.phemex.com/ws"
