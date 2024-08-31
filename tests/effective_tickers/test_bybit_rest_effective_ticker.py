import ccxt
import pytest

from crypto_exchanges.effective_tickers.bybit_rest_effective_ticker import (
    BybitRestEffectiveTicker,
    BybitRestEffectiveTickerConfig,
)


@pytest.mark.parametrize(
    "symbol, amount",
    [
        # 12.0の単位でBTC,ETHを買っていることに深い意味はない
        ("BTCUSDT", 12.0),
        ("ETHUSDT", 12.0),
    ],
)
def test_bybit_rest_effective_ticker(symbol, amount):
    bb = ccxt.bybit()
    ticker = BybitRestEffectiveTicker(
        ccxt_exchange=bb,
        config=BybitRestEffectiveTickerConfig(
            symbol=symbol, update_limit_sec=0.0001, amount=amount
        ),
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
