from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Balance:
    """証拠金を表す"""

    balance_in_btc: Decimal
    balance_in_eth: Decimal
    balance_in_jpy: Decimal
    balance_in_usd: Decimal
    balance_in_usdt: Decimal
    balance_in_usdc: Decimal
