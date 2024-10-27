from arbs_exchanges.core.domain.entities import Balance


class IBalanceRepository:
    def fetch_balance(self) -> Balance: ...
