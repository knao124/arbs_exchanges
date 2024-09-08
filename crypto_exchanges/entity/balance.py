from dataclasses import dataclass


@dataclass
class Balance:
    """残高を表す"""

    balance_in_btc: float
    balance_in_eth: float
    balance_in_jpy: float
    balance_in_usd: float
    balance_in_usdt: float
    balance_in_usdc: float
