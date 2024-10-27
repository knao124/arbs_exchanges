from arbs_exchanges.core.domain.repositories import IBalanceRepository


class BalanceGetter:
    def __init__(
        self,
        repository: IBalanceRepository,
    ):
        self._repository = repository

    def balance_in_usd(self):
        balance = self._repository.fetch_balance()
        return (
            balance.balance_in_usdt + balance.balance_in_usdc + balance.balance_in_usd
        )

    def balance_in_jpy(self):
        balance = self._repository.fetch_balance()
        return balance.balance_in_jpy
