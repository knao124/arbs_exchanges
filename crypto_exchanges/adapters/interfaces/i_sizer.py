from abc import ABC, abstractmethod
from decimal import Decimal


class ISizer(ABC):
    @abstractmethod
    def __call__(self, size: float) -> Decimal: ...
