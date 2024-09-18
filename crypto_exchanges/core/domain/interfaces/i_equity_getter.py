from abc import ABC, abstractmethod


class IEquityGetter(ABC):
    @abstractmethod
    def total_in_jpy(self) -> float: ...

    @abstractmethod
    def equity_jpy(self) -> float: ...

    @abstractmethod
    def equity_usd(self) -> float: ...
