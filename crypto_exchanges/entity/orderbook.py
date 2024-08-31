from dataclasses import dataclass


@dataclass
class OrderbookItem:
    """板の1つのレコードを表す"""

    symbol: str
    side_int: int
    price: float
    volume: float


@dataclass
class Orderbook:
    """板を表す"""

    ask: list[OrderbookItem]
    bid: list[OrderbookItem]
