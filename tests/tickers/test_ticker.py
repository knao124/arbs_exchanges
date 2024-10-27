import ccxt
import pytest

from arbs_exchanges.adapters.infra.bybit import BybitRestRepository
from arbs_exchanges.core.domain.entities import Symbol
from arbs_exchanges.core.use_cases.ticker import Ticker


@pytest.mark.parametrize(
    "symbol",
    [Symbol.BYBIT_LINEAR_BTCUSDT],
)
def test_bybit_rest_ticker(symbol):
    bb = ccxt.bybit()
    repo = BybitRestRepository(bb, 1.0)
    ticker = Ticker(
        orderbook_repository=repo,
        execution_repository=repo,
        symbol=symbol,
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
