import os

import pybotters
import pytest

from crypto_exchanges.adapters.infra.bitflyer import (
    BitflyerOrderRepository,
    BitflyerRestRepository,
    BitflyerWsRepository,
)
from crypto_exchanges.adapters.resolvers.bitflyer import init_ccxt_bitflyer
from crypto_exchanges.core.domain.entities import Symbol


@pytest.mark.asyncio
async def test_bitflyer_ws_repository():

    apis = {
        "bitflyer": [
            os.environ["BITFLYER_API_KEY_TESTNET"],
            os.environ["BITFLYER_SECRET_TESTNET"],
        ],
    }
    symbol = Symbol.BITFLYER_CFD_BTCJPY

    cc = init_ccxt_bitflyer(mode="testnet")
    order_repo = BitflyerOrderRepository(cc, symbol=symbol)
    rest_repo = BitflyerRestRepository(cc, 1.0)

    async with pybotters.Client(apis=apis) as client:
        print("initialize...")
        store = pybotters.bitFlyerDataStore()
        await store.initialize(
            client.get(
                "https://api.bitflyer.com/v1/me/getpositions",
                params={"product_code": symbol.to_exchange_symbol()},
            ),
            client.get(
                "https://api.bitflyer.com/v1/me/getchildorders",
                params={"product_code": symbol.to_exchange_symbol()},
            ),
        )
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_snapshot_FX_BTC_JPY"},
                    "id": 1,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_FX_BTC_JPY"},
                    "id": 2,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": "child_order_events"},
                    "id": 3,
                },
                {
                    "method": "subscribe",
                    "params": {
                        "channel": f"lightning_executions_{symbol.to_exchange_symbol()}"
                    },
                    "id": 4,
                },
            ],
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
        ws_repo = BitflyerWsRepository(store)
        ws_repo.fetch_positions()
        ws_repo.fetch_executions()
        ws_repo.fetch_order_book()

        # 4. ノーポジにする
        total_pos = sum(p.size_with_sign for p in rest_repo.fetch_positions(symbol))
        order_repo.create_market_order(size_with_sign=-total_pos)
