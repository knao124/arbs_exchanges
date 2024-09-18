from abc import ABC, abstractmethod
from decimal import Decimal


class ITicker(ABC):
    @abstractmethod
    def bid_price(self) -> Decimal: ...

    @abstractmethod
    def ask_price(self) -> Decimal: ...

    @abstractmethod
    def last_price(self) -> Decimal: ...
