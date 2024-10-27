from decimal import Decimal

from arbs_exchanges.core.domain.repositories import IBalanceRepository

from .ticker import Ticker


class EquityGetter:
    def __init__(
        self,
        repository: IBalanceRepository,
        usdjpy_ticker: Ticker,
    ):
        self._repository = repository
        self._usdjpy_ticker = usdjpy_ticker

    def total_in_jpy(self) -> Decimal:
        usd_jpy = self._usdjpy_ticker.last_price()
        return self.equity_usd() * usd_jpy + self.equity_jpy()

    def equity_jpy(self) -> Decimal:
        balance = self._repository.fetch_balance()
        return balance.balance_in_jpy

    def equity_usd(self) -> Decimal:
        balance = self._repository.fetch_balance()
        # usd usdt usdc の合算
        return (
            balance.balance_in_usd + balance.balance_in_usdt + balance.balance_in_usdc
        )
