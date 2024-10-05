from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Position:
    symbol: str
    entry_price: Decimal
    size_with_sign: Decimal

    @property
    def volume_abs(self) -> Decimal:
        return abs(self.size_with_sign)
