from dataclasses import dataclass
from decimal import Decimal


@dataclass
class OrderBookItem:
    """板の1つのレコードを表す"""

    symbol: str
    side_int: int
    price: Decimal
    volume: Decimal


@dataclass
class OrderBook:
    """板を表す"""

    ask: list[OrderBookItem]
    bid: list[OrderBookItem]
