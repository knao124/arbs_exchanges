from decimal import Decimal
from logging import getLogger
from typing import Optional

from arbs_exchanges.core.domain.entities import Order, Symbol
from arbs_exchanges.core.domain.repositories import IOrderRepository
from arbs_exchanges.core.use_cases.interfaces import ISizer


class Orderer:
    def __init__(
        self,
        repository: IOrderRepository,
        sizer: ISizer,
        symbol: Symbol,
    ):
        self._repository = repository
        self._sizer = sizer
        self._symbol = symbol

        self._logger = getLogger(__class__.__name__)

    def post_market_order(
        self,
        size_with_sign: Decimal,
    ) -> Optional[Order]:
        size_with_sign_rounded = self._sizer.round_size(size_with_sign)
        if not self._sizer.is_enough_size(size_with_sign_rounded):
            self._logger.debug(
                f"skip because {size_with_sign_rounded=}({size_with_sign}) < {self._sizer.min_lot_size=}"
            )
            return None
        try:
            order = self._repository.create_market_order(
                symbol=self._symbol,
                size_with_sign=size_with_sign_rounded,
            )
        except Exception as e:
            self._logger.error(f"failed to post_market_order: {e}")
            return None

        return order

    def post_limit_order(
        self,
        size_with_sign: Decimal,
        price: Decimal,
        post_only: bool,
    ) -> Order:
        try:
            order = self._repository.create_limit_order(
                symbol=self._symbol,
                size_with_sign=size_with_sign,
                price=price,
                post_only=post_only,
            )
        except Exception as e:
            raise e
        return order

    def edit_limit_order(
        self,
        order_id: str,
        size_with_sign: Decimal,
        price: Decimal,
    ) -> Order:
        try:
            order = self._repository.update_order(
                symbol=self._symbol,
                order_id=order_id,
                size_with_sign=size_with_sign,
                price=price,
            )
        except Exception as e:
            raise e
        return order

    def cancel_limit_order(
        self,
        order_id: str,
    ) -> Order:
        try:
            order = self._repository.remove_order(
                symbol=self._symbol,
                order_id=order_id,
            )
        except Exception as e:
            raise e
        return order

    def cancel_all_limit_orders(self) -> list[Order]:
        canceled_orders = []
        try:
            open_orders = self._repository.get_open_orders()
            for order in open_orders:
                canceled_order = self.cancel_limit_order(
                    order_id=order.order_id,
                    symbol=self._symbol,
                )
                canceled_orders.append(canceled_order)
        except Exception as e:
            raise e
        return canceled_orders

    def get_latest_orders(self) -> list[Order]:
        try:
            orders = self._repository.get_latest_orders()
        except Exception as e:
            raise e
        return orders

    def get_open_orders(self) -> list[Order]:
        try:
            orders = self._repository.get_open_orders()
        except Exception as e:
            raise e
        return orders
