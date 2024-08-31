import ccxt
import pytest

from crypto_exchanges.tickers.bybit_rest_ticker import (
    BybitRestTicker,
    BybitRestTickerConfig,
)


@pytest.mark.parametrize(
    "symbol",
    ["BTCUSDT", "ETHUSDT"],
)
def test_bybit_rest_ticker(symbol):
    bb = ccxt.bybit()
    ticker = BybitRestTicker(
        ccxt_exchange=bb,
        config=BybitRestTickerConfig(symbol=symbol, update_limit_sec=0.0001),
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
