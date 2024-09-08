from crypto_exchanges.repository.bybit.bybit_rest_repository import BybitRestRepository
from crypto_exchanges.resolvers.bybit.ccxt_ import init_ccxt_bybit_demo


def test_demo_bybit_rest_repository_fetch_balance():
    ccxt_bybit = init_ccxt_bybit_demo()
    repo = BybitRestRepository(ccxt_bybit)
    balance = repo.fetch_balance()

    assert type(balance.balance_in_btc) is float
