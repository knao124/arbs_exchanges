import os

import pybotters
import pytest

from arbs_exchanges.adapters.infra.phemex import (
    PhemexOrderRepository,
    PhemexRestRepository,
    PhemexWsRepository,
)
from arbs_exchanges.adapters.resolvers.phemex import (
    PHEMEX_TESTNET_WS_URL,
    init_ccxt_phemex,
)
from arbs_exchanges.core.domain.entities import Symbol


@pytest.mark.asyncio
async def test_phemex_ws_repository():

    apis = {
        "phemex_testnet": [
            os.environ["PHEMEX_API_KEY_TESTNET"],
            os.environ["PHEMEX_SECRET_TESTNET"],
        ],
    }
    symbol = Symbol.PHEMEX_LINEAR_BTCUSDT

    cc = init_ccxt_phemex(mode="testnet")
    order_repo = PhemexOrderRepository(cc, symbol=symbol)
    rest_repo = PhemexRestRepository(cc, 1.0)

    base_url = "https://testnet-api.phemex.com"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        store = pybotters.PhemexDataStore()
        print("connect...")
        await client.ws_connect(
            PHEMEX_TESTNET_WS_URL,
            send_json={
                "id": 1234,
                "method": "orderbook_p.subscribe",
                "params": ["BTCUSDT"],
            },
            hdlr_json=store.onmessage,
        )
        await client.ws_connect(
            PHEMEX_TESTNET_WS_URL,
            send_json={
                "id": 1234,
                "method": "trade_p.subscribe",
                "params": ["BTCUSDT"],
            },
            hdlr_json=store.onmessage,
        )
        await client.ws_connect(
            PHEMEX_TESTNET_WS_URL,
            send_json={
                "id": 1234,
                "method": "aop_p.subscribe",
                "params": [],
            },
            hdlr_json=store.onmessage,
        )

        # 1. ノーポジにする
        total_pos = sum(p.size_with_sign for p in rest_repo.fetch_positions(symbol))
        if total_pos != 0:
            order_repo.create_market_order(size_with_sign=-total_pos)

        # 2. 注文
        order_repo.create_market_order(size_with_sign=0.01)

        await store.positions.wait()

        # 3. repo の smoke test
        ws_repo = PhemexWsRepository(store)
        ws_repo.fetch_positions()
        ws_repo.fetch_executions()
        ws_repo.fetch_order_book()

        # 4. ノーポジにする
        total_pos = sum(p.size_with_sign for p in rest_repo.fetch_positions(symbol))
        if total_pos != 0:
            order_repo.create_market_order(size_with_sign=-total_pos)
