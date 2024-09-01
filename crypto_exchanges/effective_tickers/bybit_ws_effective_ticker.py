from dataclasses import dataclass
from typing import Protocol

import numpy as np
import pybotters

from crypto_exchanges.effective_tickers.common import _get_effective_price
from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook


@dataclass
class _BybitWsEffectiveTickerConfig:
    symbol: str
    target_volume: float = 0.1


class IBybitRepository(Protocol):
    def sorted_orderbook(self) -> Orderbook: ...
    def trades(self) -> list[Execution]: ...


class BybitWsEffectiveTicker:
    def __init__(
        self,
        repository: IBybitRepository,
        symbol: str,
        target_volume: float,
    ):
        self._repository = repository
        self._config = _BybitWsEffectiveTickerConfig(
            symbol=symbol,
            target_volume=target_volume,
        )

    def _get_bid_ask(self) -> tuple[float, float]:
        target_volume = self._config.target_volume
        orderbook = self._repository.sorted_orderbook()
        bid_price = _get_effective_price(orderbook.bid, target_volume)
        ask_price = _get_effective_price(orderbook.ask, target_volume)
        return bid_price, ask_price

    def bid_price(self) -> float:
        bid_price, _ = self._get_bid_ask()
        return bid_price

    def ask_price(self) -> float:
        _, ask_price = self._get_bid_ask()
        return ask_price

    def last_price(self) -> float:
        trades = self._repository.trades()
        if len(trades) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return trades[-1].price
