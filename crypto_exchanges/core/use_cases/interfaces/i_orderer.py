from abc import ABC, abstractmethod


class IOrderer(ABC):
    @abstractmethod
    def post_market_order(
        self, side_int: int, size: float, params: dict = {}
    ) -> dict: ...

    @abstractmethod
    def post_limit_order(
        self,
        side_int: int,
        size: float,
        price: float,
        post_only: bool = False,
        params: dict = {},
    ) -> dict: ...

    @abstractmethod
    def cancel_limit_order(self, order_id: str) -> dict: ...

    @abstractmethod
    def edit_limit_order(
        self, order_id: str, side_int: int, size: float, price: float, params: dict = {}
    ) -> dict: ...

    @abstractmethod
    def fetch_latest_orders(self) -> list: ...

    @abstractmethod
    def fetch_open_orders(self) -> list: ...

    @abstractmethod
    def cancel_all_orders(self) -> None: ...
