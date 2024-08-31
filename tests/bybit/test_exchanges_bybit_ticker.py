import asyncio
import os

import ccxt
import pytest

from crypto_exchanges import bybit
from crypto_exchanges.utils import kill_all_asyncio_tasks

from .utils import skip_if_secret_not_set_bybit

"""
See the following links to check the min lot size
BTCUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=BTCUSDT
ETHUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=ETHUSDT
"""


@pytest.mark.parametrize(
    "symbol",
    ["BTCUSDT", "ETHUSDT"],
)
def test_bybit_rest_ticker(symbol):
    bb = ccxt.bybit()
    ticker = bybit.BybitRestTicker(
        ccxt_exchange=bb,
        config=bybit.BybitRestTickerConfig(symbol=symbol, update_limit_sec=0.0001),
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0


@pytest.mark.parametrize(
    "symbol, amount",
    [
        # 12.0の単位でBTC,ETHを買っていることに深い意味はない
        ("BTCUSDT", 12.0),
        ("ETHUSDT", 12.0),
    ],
)
def test_bybit_rest_effective_ticker(symbol, amount):
    bb = ccxt.bybit()
    ticker = bybit.BybitRestEffectiveTicker(
        ccxt_exchange=bb,
        config=bybit.BybitRestEffectiveTickerConfig(
            symbol=symbol, update_limit_sec=0.0001, amount=amount
        ),
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0


@skip_if_secret_not_set_bybit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "symbol, settlement_symbol, lot_size",
    [
        # 12.0の単位でBTC,ETHを買っていることに深い意味はない
        ("BTCUSDT", "USDT", 0.0010),
        ("ETHUSDT", "USDT", 0.010),
    ],
)
async def test_bybit_ws_ticker(symbol, settlement_symbol, lot_size):
    if "USDT" in symbol:
        client, store = await bybit.start_bybit_ws_linear(
            api_key=os.environ["BYBIT_API_KEY"],
            secret=os.environ["BYBIT_SECRET"],
            symbol=symbol,
            testnet=True,
        )
    else:
        client, store = await bybit.start_bybit_ws_inverse(
            api_key=os.environ["BYBIT_API_KEY"],
            secret=os.environ["BYBIT_SECRET"],
            symbol=symbol,
            testnet=True,
        )

    ticker = bybit.BybitWsTicker(
        store=store,
        symbol=symbol,
    )

    # rarely executed on testnet, so trade by myself
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)
    try:
        bb.set_position_mode(hedged=False, symbol=symbol)
    except BaseException:
        ...
    orderer = bybit.BybitOrderer(
        ccxt_exchange=bb,
        symbol=symbol,
        settlement_symbol=settlement_symbol,
    )
    orderer.post_market_order(side_int=1, size=lot_size)
    orderer.post_market_order(side_int=-1, size=lot_size)

    await asyncio.sleep(2)

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0

    await kill_all_asyncio_tasks()


@skip_if_secret_not_set_bybit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "symbol, settlement_symbol, lot_size, amount",
    [
        # 12.0の単位でBTC,ETHを買っていることに深い意味はない
        ("BTCUSDT", "USDT", 0.0010, 12.0),
        ("ETHUSDT", "USDT", 0.010, 12.0),
    ],
)
async def test_bybit_ws_effective_ticker(symbol, settlement_symbol, lot_size, amount):
    if "USDT" in symbol:
        client, store = await bybit.start_bybit_ws_linear(
            api_key=os.environ["BYBIT_API_KEY"],
            secret=os.environ["BYBIT_SECRET"],
            symbol=symbol,
            testnet=True,
        )
    else:
        client, store = await bybit.start_bybit_ws_inverse(
            api_key=os.environ["BYBIT_API_KEY"],
            secret=os.environ["BYBIT_SECRET"],
            symbols=symbol,
            testnet=True,
        )

    ticker = bybit.BybitWsEffectiveTicker(
        store=store,
        config=bybit.BybitWsEffectiveTickerConfig(
            symbol=symbol,
            amount=amount,
        ),
    )

    # rarely executed on testnet, so trade by myself
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)
    try:
        bb.set_position_mode(hedged=False, symbol=symbol)
    except BaseException:
        ...
    orderer = bybit.BybitOrderer(
        ccxt_exchange=bb,
        symbol=symbol,
        settlement_symbol=settlement_symbol,
    )
    orderer.post_market_order(side_int=1, size=lot_size)
    orderer.post_market_order(side_int=-1, size=lot_size)

    await asyncio.sleep(2)
    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0

    await kill_all_asyncio_tasks()
