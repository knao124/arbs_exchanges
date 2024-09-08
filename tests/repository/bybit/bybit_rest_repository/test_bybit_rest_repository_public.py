import ccxt

from crypto_exchanges.repository.bybit.bybit_rest_repository import BybitRestRepository


def test_bybit_rest_repository_fetch_order_book():
    repo = BybitRestRepository(ccxt.bybit())
    orderbook = repo.fetch_order_book("BTCUSDT", limit=1)

    assert len(orderbook.bid) == 1
    assert len(orderbook.ask) == 1


def test_bybit_rest_repository_fetch_trades():
    repo = BybitRestRepository(ccxt.bybit())
    trades = repo.fetch_trades("BTCUSDT", limit=1)

    assert len(trades) == 1
