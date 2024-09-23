from abc import ABC, abstractmethod
from decimal import Decimal

from crypto_exchanges.core.domain.entities import Order, Symbol


class IOrderRepository(ABC):
    @abstractmethod
    def create_market_order(
        self,
        symbol: Symbol,
        size_with_sign: Decimal,
    ) -> Order:
        pass

    @abstractmethod
    def create_limit_order(
        self,
        symbol: Symbol,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:
        pass

    @abstractmethod
    def update_order(
        self,
        symbol: Symbol,
        order_id: str,
        size_with_sign: Decimal,
        price: Decimal,
    ) -> Order:
        pass

    @abstractmethod
    def remove_order(
        self,
        symbol: Symbol,
        order_id: str,
    ) -> Order:
        pass

    @abstractmethod
    def get_open_orders(
        self,
        symbol: Symbol,
    ) -> list[Order]:
        pass

    @abstractmethod
    def get_latest_orders(
        self,
        symbol: Symbol,
    ) -> list[Order]:
        pass
