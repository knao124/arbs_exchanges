from typing import Protocol

from arbs_exchanges.core.domain.repositories import (
    IPositionGetter,
    IPositionRepository,
)


class WsPositionGetter(IPositionGetter):
    def __init__(
        self,
        repository: IPositionRepository,
        symbol: str,
    ):

        self._repository = repository
        self._symbol = symbol

    def current_position(self) -> float:
        """
        現在のポジションを返す

        Returns:
            float or int: ポジションの大きさ
        """
        position = self._repository.position()
        return position.size

    def avg_price(self) -> float:
        """
        ポジションの平均取得単価を返す

        Returns:
            float: ポジションをもっていない場合は np.nan が返る
        """
        position = self._repository.position()
        return position.entry_price
