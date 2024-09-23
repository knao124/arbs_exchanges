from abc import ABC, abstractmethod
from decimal import Decimal


class ISizer(ABC):
    @abstractmethod
    def round_size(self, size: float) -> Decimal: ...

    @abstractmethod
    def is_enough_size(self, size: float) -> bool: ...
