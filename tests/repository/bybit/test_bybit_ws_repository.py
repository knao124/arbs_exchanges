# %%
import os

import pybotters
import pytest
from dotenv import load_dotenv

from crypto_exchanges.adapters.infra.bybit import (
    BybitOrderRepository,
    BybitRestRepository,
    BybitWsRepository,
)
from crypto_exchanges.adapters.resolvers.bybit import init_ccxt_bybit
from crypto_exchanges.core.domain.entities import Symbol
from crypto_exchanges.utils import kill_all_asyncio_tasks

load_dotenv()


@pytest.mark.asyncio
async def test_bybit_ws_repository():
    symbol = Symbol.BYBIT_LINEAR_BTCUSDT

    apis = {
        "bybit_testnet": [
            os.environ["BYBIT_API_KEY_TESTNET"],
            os.environ["BYBIT_SECRET_TESTNET"],
        ],
    }
    cc = init_ccxt_bybit(mode="testnet")

    rest_repo = BybitRestRepository(cc, 1.0)
    order_repo = BybitOrderRepository(cc, symbol=symbol)

    async with pybotters.Client(apis=apis) as client:
        store = pybotters.BybitDataStore()
        print("initialize public...")
        await client.ws_connect(
            "wss://stream-testnet.bybit.com/v5/public/linear",
            send_json={
                "op": "subscribe",
                "args": [
                    f"orderbook.50.{symbol.to_exchange_symbol()}",
                    f"publicTrade.{symbol.to_exchange_symbol()}",
                ],
            },
            hdlr_json=store.onmessage,
        )
        print("initialize private...")
        await client.ws_connect(
            "wss://stream-testnet.bybit.com/v5/private",
            send_json={
                "op": "subscribe",
                "args": [
                    "position",
                ],
            },
            hdlr_json=store.onmessage,
        )
        print("initialize done")

        ws_repo = BybitWsRepository(store=store)

        # 1. ノーポジにする
        positions = rest_repo.fetch_positions(symbol=symbol)
        total_pos = sum(p.size_with_sign for p in positions)
        if total_pos != 0:
            order_repo.create_market_order(size_with_sign=-total_pos)

        # 2. 買う
        order_repo.create_market_order(size_with_sign=0.001)

        # 3. smoke test
        print(
            "waiting ... "
        )  # 注文からpositionに反映されるまで少しラグがあるので待てる
        await store.position.wait()

        # position
        pos = ws_repo.fetch_positions()
        assert len(pos) != 0

        # executions
        execs = ws_repo.fetch_executions()
        assert len(execs) != 0

        # order_book
        order_book = ws_repo.fetch_order_book()
        assert len(order_book.ask) != 0
        assert len(order_book.bid) != 0

        # 4. ノーポジにする
        positions = rest_repo.fetch_positions(symbol=symbol)
        total_pos = sum(p.size_with_sign for p in positions)
        if total_pos != 0:
            order_repo.create_market_order(size_with_sign=-total_pos)

    await kill_all_asyncio_tasks()
