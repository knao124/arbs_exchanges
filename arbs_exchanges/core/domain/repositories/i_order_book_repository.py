from abc import ABC, abstractmethod

from arbs_exchanges.core.domain.entities import OrderBook, Symbol


class IOrderBookRepository(ABC):
    @abstractmethod
    def fetch_order_book(self, symbol: Symbol) -> OrderBook: ...
