import pybotters
import pytest

from crypto_exchanges.repository.bybit.bybit_ws_repository import BybitWsRepository
from crypto_exchanges.utils import kill_all_asyncio_tasks


@pytest.mark.asyncio
async def test_bybit_ws_repository_real():
    """BybitのWebsocketのRepositoryを実際のendpointに接続してテストする"""

    async with pybotters.Client() as client:
        # データストアを作成
        store = pybotters.BybitDataStore()
        repo = BybitWsRepository(store=store)
        await client.ws_connect(
            "wss://stream.bybit.com/v5/public/linear",
            send_json={
                "op": "subscribe",
                "args": [
                    "orderbook.50.BTCUSDT",
                    "publicTrade.BTCUSDT",
                    "position.BTCUSDT",
                ],
            },
            hdlr_json=store.onmessage,
        )

        # orderbook
        await store.orderbook.wait()
        orderbook = repo.sorted_orderbook()
        assert len(orderbook.bid) > 0
        assert len(orderbook.ask) > 0

        # trade
        await store.trade.wait()
        trades = repo.trades()
        assert len(trades) > 0

        await store.position.wait()
        position = repo.position()
        assert position.symbol == "BTCUSDT"
        assert position.side_int == 1
        assert position.price == 59065.80
        assert position.volume == 0.001

    await kill_all_asyncio_tasks()


# %%
import asyncio
import os

import pybotters
from dotenv import load_dotenv

load_dotenv()


async def main():
    apis = {
        "bybit_demo": [
            os.environ["BYBIT_API_KEY"],
            os.environ["BYBIT_SECRET"],
        ],
    }

    async with pybotters.Client(apis=apis) as client:
        store = pybotters.BybitDataStore()
        # repo = BybitWsRepository(store=store)
        await client.ws_connect(
            # testnetでやってみよう
            "wss://stream-demo.bybit.com/v5/private",
            send_json={
                "op": "subscribe",
                "args": [
                    "position",
                ],
            },
            hdlr_json=store.onmessage,
        )
        await store.position.wait()
        print(store.position.find())


await main()
