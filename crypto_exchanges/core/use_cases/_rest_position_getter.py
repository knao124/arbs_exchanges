from decimal import Decimal

import ccxt

from arbs_exchanges.core.domain.repositories import IPositionRepository
from arbs_exchanges.core.exceptions import UnexpectedSpecError
from arbs_exchanges.core.use_cases.interfaces import IPositionGetter


class PositionGetter(IPositionGetter):
    def __init__(
        self,
        ccxt_exchange: ccxt.bybit,
        symbol: str,
    ):
        self._bybit = ccxt_exchange
        self._symbol = symbol

    def current_position(self) -> Decimal:
        positions = self._bybit.fetch_positions(symbols=[self._symbol])
        if len(positions) == 0:
            return Decimal(0)

        total = Decimal(0)
        for pos in positions:
            base_size = pos["contracts"]
            if base_size is None:
                continue
            side_sign = 1 if pos["side"] == "long" else -1
            total += Decimal(base_size) * side_sign
        return total

    def avg_price(self) -> Decimal:
        positions = self._bybit.fetch_positions(symbols=[self._symbol])
        if len(positions) == 0:
            # 未定義のときはnanを返す
            return Decimal("nan")

        if len(positions) > 1:
            raise UnexpectedSpecError(f"ポジションが複数ある, {positions=}")

        entry_price = positions[0]["entryPrice"]
        return Decimal(entry_price)
