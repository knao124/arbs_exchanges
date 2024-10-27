import os
from typing import Literal

import ccxt
from dotenv import load_dotenv

load_dotenv()


def init_ccxt_bitflyer(
    mode: Literal["testnet", "real"],
) -> ccxt.bitflyer:
    """biftlyerのccxt exchangeを返す

    Args:
        default_type (str): デフォルトの取引タイプ. future or spot

    Returns:
        ccxt.bitflyer: bitflyerのccxt exchange
    """
    if mode == "testnet":
        return ccxt.bitflyer(
            {
                "apiKey": os.environ["BITFLYER_API_KEY_TESTNET"],
                "secret": os.environ["BITFLYER_SECRET_TESTNET"],
            }
        )
    elif mode == "real":
        return ccxt.bitflyer(
            {
                "apiKey": os.environ["BITFLYER_API_KEY"],
                "secret": os.environ["BITFLYER_SECRET"],
            }
        )

    raise ValueError(f"invalid mode: {mode}")
