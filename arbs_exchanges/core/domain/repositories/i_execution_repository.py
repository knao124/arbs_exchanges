from abc import ABC, abstractmethod
from typing import Optional

from arbs_exchanges.core.domain.entities import Execution, Symbol


class IExecutionRepository(ABC):
    @abstractmethod
    def fetch_executions(
        self, symbol: Symbol, limit: Optional[int] = None
    ) -> list[Execution]: ...
