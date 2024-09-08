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

    await kill_all_asyncio_tasks()
