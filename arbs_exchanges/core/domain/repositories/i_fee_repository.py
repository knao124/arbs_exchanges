from arbs_exchanges.core.domain.entities import Fee, Symbol


class IFeeRepository:
    def fetch_fee(self, symbol: Symbol) -> Fee: ...
