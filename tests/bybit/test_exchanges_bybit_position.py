import asyncio
import os
import time

import ccxt
import pytest

from crypto_exchanges import bybit

from .utils import skip_if_secret_not_set_bybit

"""
See the following links to check the min lot size
BTCUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=BTCUSDT
ETHUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=ETHUSDT
"""


@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol, position_type",
    [("BTCUSDT", float), ("ETHUSDT", float)],
)
def test_bybit_rest_position_getter(symbol, position_type):
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)

    getter = bybit.BybitRestPositionGetter(
        ccxt_exchange=bb,
        symbol=symbol,
    )

    assert type(getter.current_position()) is position_type


@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol, lot_size",
    [("BTCUSDT", 0.0010), ("ETHUSDT", 0.010)],
)
def test_bybit_rest_position_getter_avg_price(symbol, lot_size):
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)

    getter = bybit.BybitRestPositionGetter(
        ccxt_exchange=bb,
        symbol=symbol,
    )

    # ロングポジを作る
    orderer = bybit.BybitOrderer(
        ccxt_exchange=bb,
        symbol=symbol,
        settlement_symbol="USDT",
    )
    orderer.post_market_order(side_int=1, size=lot_size)
    time.sleep(0.100)

    # 平均取得単価が返ってくる
    assert getter.avg_price() > 0

    # teardown
    pos = getter.current_position()
    orderer.post_market_order(side_int=1 if pos < 0 else -1, size=abs(pos))
    time.sleep(0.100)
    assert getter.current_position() == 0

    # ノーポジのときはNone
    assert getter.avg_price() is None


@pytest.mark.asyncio
@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol, settlement_symbol, lot_size",
    [("BTCUSDT", "USDT", 0.0010), ("ETHUSDT", "USDT", 0.010)],
)
async def test_bybit_ws_position_getter(symbol, settlement_symbol, lot_size):
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

    try:
        await asyncio.wait_for(store.wait(), timeout=1.0)
    except asyncio.TimeoutError:
        print("asyncio.wait_for(store.wait(), timeout=1.0) timeout")

    getter = bybit.BybitWsPositionGetter(
        store=store,
        symbol=symbol,
    )

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

    pos = getter.current_position()

    orderer.post_market_order(side_int=1, size=lot_size)
    await asyncio.sleep(0.100)
    assert getter.current_position() == pos + lot_size
    assert getter.avg_price() > 0

    orderer.post_market_order(side_int=-1, size=lot_size)
    await asyncio.sleep(0.100)
    assert getter.current_position() == pos

    if pos != 0:
        orderer.post_market_order(side_int=1 if pos < 0 else -1, size=abs(pos))
        await asyncio.sleep(0.100)

    assert getter.current_position() == 0
    assert getter.avg_price() is None
    await client.close()
