# %%
from crypto_exchanges.repository.bybit.bybit_rest_repository import BybitRestRepository


def test_mock_bybit_rest_repository_fetch_balance():
    # 依存先のccxtをmockする
    class MockCcxt:
        def fetch_balance(self):
            return {
                "BTC": {
                    "free": 1.0,
                    "used": 0.0,
                    "total": 1.0,
                },
                "USDT": {
                    "free": 100,
                    "used": 0,
                    "total": 100,
                },
                "JPY": {
                    "free": 300,
                    "used": 0,
                    "total": 300,
                },
            }

    ccxt_bybit = MockCcxt()
    repo = BybitRestRepository(ccxt_bybit)
    balance = repo.fetch_balance()

    # 想定どおりにBalanceになっているか確認
    assert balance.balance_in_btc == 1.0
    assert balance.balance_in_usdt == 100
    assert balance.balance_in_jpy == 300
