from abc import ABC, abstractmethod


class IBalanceGetter(ABC):
    @abstractmethod
    def balance(self) -> float: ...
