from abc import ABC, abstractmethod


class IOrderLinkIdGenerator(ABC):
    @abstractmethod
    def generate(self) -> str: ...
