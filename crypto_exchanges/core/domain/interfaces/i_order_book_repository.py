from abc import ABC, abstractmethod

from crypto_exchanges.core.domain.entities import OrderBook


class IOrderBookRepository(ABC):
    @abstractmethod
    def fetch_order_book(self) -> OrderBook: ...
