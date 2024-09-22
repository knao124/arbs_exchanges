from abc import ABC, abstractmethod
from typing import Optional

from crypto_exchanges.core.domain.entities import Execution


class IExecutionRepository(ABC):
    @abstractmethod
    def fetch_executions(
        self, symbol: str, limit: Optional[int] = None
    ) -> list[Execution]: ...
