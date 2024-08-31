from crypto_exchanges.effective_tickers.bybit_ws_effective_ticker import (
    BybitWsEffectiveTicker,
)
from crypto_exchanges.pybotters.bybit_mock_datastore import BybitMockDataStore
from crypto_exchanges.pybotters.bybit_repository import BybitRepository


def test_bybit_ws_effective_ticker():
    mock_store = BybitMockDataStore()
    ticker = BybitWsEffectiveTicker(
        repository=BybitRepository(store=mock_store),
        symbol="BTCUSDT",
        target_volume=0.5,
    )
    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
