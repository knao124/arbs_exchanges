from decimal import Decimal

from arbs_exchanges.core.domain.repositories import IPositionRepository
from arbs_exchanges.core.exceptions import UnexpectedSpecError


class PositionGetter:
    def __init__(
        self,
        repository: IPositionRepository,
        symbol: str,
    ):

        self._repository = repository
        self._symbol = symbol

    def current_position(self) -> Decimal:
        """
        現在のポジションを返す

        Returns:
            float or int: ポジションの大きさ
        """
        positions = self._repository.fetch_positions()
        if len(positions) == 0:
            return Decimal(0)

        total = Decimal(0)
        for pos in positions:
            base_size = pos.size
            if base_size is None:
                continue
            total += Decimal(base_size) * pos.side_int
        return total

    def avg_price(self) -> Decimal:
        """
        ポジションの平均取得単価を返す

        Returns:
            float: ポジションをもっていない場合は np.nan が返る
        """
        positions = self._repository.fetch_positions()
        if len(positions) == 0:
            return Decimal("nan")
        elif len(positions) > 1:
            raise UnexpectedSpecError(f"ポジションが複数ある, {positions=}")
        position = positions[0]
        return position.entry_price
