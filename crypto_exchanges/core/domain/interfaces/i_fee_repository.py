from crypto_exchanges.core.domain.entities import Fee


class IFeeRepository:
    def fetch_fee(self) -> Fee: ...
