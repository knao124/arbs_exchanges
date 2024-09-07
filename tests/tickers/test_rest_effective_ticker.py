import ccxt
import pytest

from crypto_exchanges.rest.bybit_rest_repository import BybitRestRepository
from crypto_exchanges.tickers.rest_effective_ticker import RestEffectiveTicker


@pytest.mark.parametrize(
    "symbol, target_volume",
    [
        # 12.0の単位でBTC,ETHを買っていることに深い意味はない
        ("BTCUSDT", 12.0),
        ("ETHUSDT", 12.0),
    ],
)
def test_bybit_rest_effective_ticker(symbol, target_volume):
    bb = ccxt.bybit()
    repo = BybitRestRepository(bb)
    ticker = RestEffectiveTicker(
        repository=repo,
        symbol=symbol,
        target_volume=target_volume,
        update_limit_sec=0.0001,
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
