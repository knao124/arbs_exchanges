from abc import ABC, abstractmethod
from decimal import Decimal


class IPositionGetter(ABC):
    @abstractmethod
    def current_position(self) -> Decimal:
        """
        現在のポジションを返す

        Returns:
            Decimal: ポジションの大きさ
        """
        ...

    @abstractmethod
    def avg_price(self) -> Decimal:
        """
        ポジションの平均取得単価を返す

        Returns:
            Decimal: ポジションをもっていない場合は Decimal("nan") が返る
        """
        ...
