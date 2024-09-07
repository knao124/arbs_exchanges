from dataclasses import dataclass
from typing import Protocol

from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook
from crypto_exchanges.tickers.common import get_effective_price


class IWsRepository(Protocol):
    def sorted_orderbook(self) -> Orderbook: ...
    def trades(self) -> list[Execution]: ...


@dataclass
class _WsEffectiveTickerConfig:
    symbol: str
    target_volume: float


class WsEffectiveTicker:
    def __init__(
        self,
        repository: IWsRepository,
        symbol: str,
        target_volume: float,
    ):
        self._repository = repository
        self._config = _WsEffectiveTickerConfig(
            symbol=symbol,
            target_volume=target_volume,
        )

    def _get_bid_ask(self) -> tuple[float, float]:
        target_volume = self._config.target_volume
        orderbook = self._repository.sorted_orderbook()
        bid_price = get_effective_price(orderbook.bid, target_volume)
        ask_price = get_effective_price(orderbook.ask, target_volume)
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
