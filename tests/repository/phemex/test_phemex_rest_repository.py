# %%
from arbs_exchanges.adapters.infra.phemex.phemex_rest_repository import (
    PhemexRestRepository,
)
from arbs_exchanges.adapters.resolvers.phemex import init_ccxt_phemex
from arbs_exchanges.core.domain.entities import Symbol


def test_phemex_rest_resository_smoke():
    ccxt_phemex = init_ccxt_phemex("testnet")
    repo = PhemexRestRepository(ccxt_phemex, 1.0)
    order_book = repo.fetch_order_book(Symbol.PHEMEX_LINEAR_BTCUSDT)
    assert order_book.ask[0].price > 0

    balance = repo.fetch_balance()
    assert balance.balance_in_usdt > 0

    fee = repo.fetch_fee(Symbol.PHEMEX_LINEAR_BTCUSDT)
    assert fee.maker > 0
    assert fee.taker > 0

    positions = repo.fetch_positions(Symbol.PHEMEX_LINEAR_BTCUSDT)
    assert positions[0].symbol == Symbol.PHEMEX_LINEAR_BTCUSDT

    executions = repo.fetch_executions(Symbol.PHEMEX_LINEAR_BTCUSDT)
    assert executions[0].symbol == Symbol.PHEMEX_LINEAR_BTCUSDT
