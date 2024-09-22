from abc import ABC, abstractmethod

from crypto_exchanges.core.domain.entities import Position


class IPositionRepository(ABC):
    @abstractmethod
    def fetch_positions(self) -> list[Position]: ...
