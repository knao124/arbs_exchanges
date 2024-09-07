from crypto_exchanges.tickers.ws_effective_ticker import WsEffectiveTicker
from crypto_exchanges.ws.bybit_mock_datastore import BybitMockDataStore
from crypto_exchanges.ws.bybit_ws_repository import BybitWsRepository


def test_bybit_ws_effective_ticker():
    mock_store = BybitMockDataStore()
    repo = BybitWsRepository(store=mock_store)
    ticker = WsEffectiveTicker(
        repository=repo,
        symbol="BTCUSDT",
        target_volume=0.5,
    )
    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
