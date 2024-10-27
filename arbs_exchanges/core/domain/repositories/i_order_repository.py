from abc import ABC, abstractmethod
from decimal import Decimal

from arbs_exchanges.core.domain.entities import Order


class IOrderRepository(ABC):
    @abstractmethod
    def create_market_order(
        self,
        size_with_sign: Decimal,
    ) -> Order:
        pass

    @abstractmethod
    def create_limit_order(
        self,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:
        pass

    @abstractmethod
    def update_order(
        self,
        order_id: str,
        size_with_sign: Decimal,
        price: Decimal,
    ) -> Order:
        pass

    @abstractmethod
    def remove_order(
        self,
        order_id: str,
    ) -> Order:
        pass

    @abstractmethod
    def remove_all_orders(
        self,
    ) -> bool:
        pass

    @abstractmethod
    def get_open_orders(
        self,
    ) -> list[Order]:
        pass

    @abstractmethod
    def get_latest_orders(
        self,
    ) -> list[Order]:
        pass
