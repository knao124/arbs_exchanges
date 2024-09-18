from abc import ABC, abstractmethod

from crypto_exchanges.core.domain.entities import Execution


class IExecutionRepository(ABC):
    @abstractmethod
    def fetch_executions(self) -> list[Execution]: ...
