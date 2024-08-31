import os

import ccxt
import pytest

from crypto_exchanges import bybit

from .utils import skip_if_secret_not_set_bybit


@pytest.mark.asyncio
@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol",
    [("BTCUSDT"), ("ETHUSDT")],
)
async def test_bybit_fee_getter(symbol):
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)

    getter = bybit.BybitFeeGetter(ccxt_exchange=bb, symbol=symbol)
    assert type(getter.maker_fee()) is float
    assert type(getter.taker_fee()) is float
