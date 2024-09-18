from abc import ABC, abstractmethod

from crypto_exchanges.core.domain.entities import Position


class IPositionRepository(ABC):
    @abstractmethod
    def position(self) -> Position: ...
