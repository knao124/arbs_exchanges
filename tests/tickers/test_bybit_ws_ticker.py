from crypto_exchanges.pybotters.bybit_mock_datastore import BybitMockDataStore
from crypto_exchanges.pybotters.bybit_repository import BybitRepository
from crypto_exchanges.tickers.bybit_ws_ticker import BybitWsTicker


def test_bybit_ws_ticker():
    mock_store = BybitMockDataStore()
    repo = BybitRepository(store=mock_store)
    ticker = BybitWsTicker(repository=repo, symbol="BTCUSDT")
    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
