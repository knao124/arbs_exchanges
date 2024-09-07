import ccxt
import pytest

from crypto_exchanges.repository.bybit.bybit_rest_repository import BybitRestRepository
from crypto_exchanges.tickers.rest_ticker import RestTicker


@pytest.mark.parametrize(
    "symbol",
    ["BTCUSDT", "ETHUSDT"],
)
def test_bybit_rest_ticker(symbol):
    bb = ccxt.bybit()
    repo = BybitRestRepository(bb)
    ticker = RestTicker(
        repository=repo,
        symbol=symbol,
        update_limit_sec=0.0001,
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
