from dataclasses import dataclass
from decimal import Decimal

import pandas as pd


@dataclass
class Execution:
    """約定を表す"""

    id: str
    ts: pd.Timestamp
    symbol: str
    side_int: int
    price: Decimal
    volume: Decimal
