from dataclasses import dataclass
from decimal import Decimal

from crypto_exchanges.core.domain.entities.order_type import OrderType
from crypto_exchanges.core.domain.entities.symbol import Symbol


@dataclass
class Order:
    order_type: OrderType
    order_id: str
    symbol: Symbol
    size_with_sign: Decimal
    price: Decimal
