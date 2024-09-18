from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Position:
    symbol: str
    side_int: int
    entry_price: Decimal
    size: Decimal

    @property
    def volume_abs(self) -> Decimal:
        return abs(self.size)
