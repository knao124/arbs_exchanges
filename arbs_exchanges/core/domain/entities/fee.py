from dataclasses import dataclass
from decimal import Decimal

from .symbol import Symbol


@dataclass
class Fee:
    symbol: Symbol
    # 小数点の手数料率(%ではない)
    maker: Decimal
    # 小数点の手数料率(%ではない)
    taker: Decimal
