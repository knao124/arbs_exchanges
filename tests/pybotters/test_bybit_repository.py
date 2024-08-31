import pybotters
import pytest

from crypto_exchanges.pybotters.bybit_mock_datastore import BybitMockDataStore
from crypto_exchanges.pybotters.bybit_repository import BybitRepository
from crypto_exchanges.tickers.bybit_ws_ticker import BybitWsTicker
from crypto_exchanges.utils import kill_all_asyncio_tasks


@pytest.mark.asyncio
async def test_pybotters_bybit_datastore():
    async with pybotters.Client() as client:
        store = pybotters.BybitDataStore()
        repo = BybitRepository(store=store)
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
