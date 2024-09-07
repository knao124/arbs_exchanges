from crypto_exchanges.tickers.ws_ticker import WsTicker
from crypto_exchanges.ws.bybit_mock_datastore import BybitMockDataStore
from crypto_exchanges.ws.bybit_ws_repository import BybitWsRepository


def test_bybit_ws_ticker():
    mock_store = BybitMockDataStore()
    repo = BybitWsRepository(store=mock_store)
    ticker = WsTicker(repository=repo, symbol="BTCUSDT")
    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
