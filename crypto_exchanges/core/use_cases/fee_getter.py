import time
from decimal import Decimal

import ccxt

from arbs_exchanges.core.domain.repositories import IFeeRepository


class FeeGetter:
    def __init__(
        self,
        repository: IFeeRepository,
        update_limit_sec: float = 60,
    ):
        self._repository = repository
        self._update_limit_sec = update_limit_sec

    def fetch_maker_fee(self, symbol: str) -> Decimal:
        fee = self._repository.fetch_fee(symbol=symbol)
        return fee.maker

    def fetch_taker_fee(self, symbol: str) -> Decimal:
        fee = self._repository.fetch_fee(symbol=symbol)
        return fee.taker
