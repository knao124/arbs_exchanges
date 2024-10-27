import ccxt
import pytest

from arbs_exchanges.adapters.infra.bybit import BybitRestRepository
from arbs_exchanges.core.domain.entities import Symbol
from arbs_exchanges.core.use_cases.effective_ticker import EffectiveTicker


@pytest.mark.parametrize(
    "symbol, target_volume",
    [
        (Symbol.BYBIT_LINEAR_BTCUSDT, 0.001),
    ],
)
def test_bybit_rest_effective_ticker(symbol, target_volume):
    bb = ccxt.bybit()
    repo = BybitRestRepository(bb, 1.0)
    ticker = EffectiveTicker(
        orderbook_repository=repo,
        execution_repository=repo,
        symbol=symbol,
        target_volume=target_volume,
    )

    assert ticker.bid_price() > 0
    assert ticker.ask_price() > 0
    assert ticker.last_price() > 0
