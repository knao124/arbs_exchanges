import os

import pytest

from crypto_exchanges import bybit

from .utils import skip_if_secret_not_set_bybit


@pytest.mark.parametrize(
    "symbol",
    [
        ("BTCUSDT"),
        ("ETHUSDT"),
    ],
)
@pytest.mark.asyncio
@skip_if_secret_not_set_bybit
async def test_start_bybit_ws_linear_smoke(symbol):
    client, store = await bybit.start_bybit_ws_linear(
        api_key=os.environ["BYBIT_API_KEY"],
        secret=os.environ["BYBIT_SECRET"],
        symbol=symbol,
        testnet=True,
    )

    await client.close()
