from dataclasses import dataclass

import pandas as pd


@dataclass
class Execution:
    """約定を表す"""

    id: str
    ts: pd.Timestamp
    symbol: str
    side_int: int
    price: float
    volume: float
