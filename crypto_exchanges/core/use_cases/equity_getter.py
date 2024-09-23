from crypto_exchanges.core.domain.repositories import IBalanceRepository
from crypto_exchanges.core.use_cases import Ticker


class EquityGetter:
    def __init__(
        self,
        repository: IBalanceRepository,
        usdjpy_ticker: Ticker,
    ):
        self._repository = repository
        self._usdjpy_ticker = usdjpy_ticker

    def total_in_jpy(self) -> float:
        usd_jpy = self._usdjpy_ticker.last_price()
        return self.equity_usd() * usd_jpy

    def equity_jpy(self):
        """
        海外の取引所にJPYは預けない運用のため、JPYのequityは0
        """
        return 0.0

    def equity_usd(self):
        balance = self._repository.fetch_balance()
        return float(balance["info"]["result"]["USDT"]["equity"])
