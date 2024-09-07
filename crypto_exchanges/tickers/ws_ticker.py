from dataclasses import dataclass
from typing import Protocol

import numpy as np

from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook


class IWsRepository(Protocol):
    def sorted_orderbook(self) -> Orderbook: ...
    def trades(self) -> list[Execution]: ...


@dataclass
class _WsTickerConfig:
    symbol: str


class WsTicker:
    def __init__(
        self,
        repository: IWsRepository,
        symbol: str,
    ):

        self._repository = repository
        self._config = _WsTickerConfig(symbol=symbol)

    def bid_price(self) -> float:
        orderbook = self._repository.sorted_orderbook()

        if len(orderbook.bid) == 0:
            return np.nan
        return float(orderbook.bid[0].price)

    def ask_price(self) -> float:
        orderbook = self._repository.sorted_orderbook()

        if len(orderbook.ask) == 0:
            return np.nan
        return float(orderbook.ask[0].price)

    def last_price(self) -> float:
        trades = self._repository.trades()

        # 履歴がない場合はask bidの中央を返す
        if len(trades) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return float(trades[-1].price)
