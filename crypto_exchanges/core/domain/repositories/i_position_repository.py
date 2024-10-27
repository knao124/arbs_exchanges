from abc import ABC, abstractmethod

from arbs_exchanges.core.domain.entities import Position, Symbol


class IPositionRepository(ABC):
    @abstractmethod
    def fetch_positions(self, symbol: Symbol) -> list[Position]: ...
