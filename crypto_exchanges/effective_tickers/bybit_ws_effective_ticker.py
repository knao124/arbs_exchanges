from dataclasses import dataclass
from typing import Protocol

import numpy as np
import pybotters

from crypto_exchanges.entity.execution import Execution
from crypto_exchanges.entity.orderbook import Orderbook, OrderbookItem


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


def _get_effective_price(
    orderbook_items: list[OrderbookItem],
    target_volume: float,
) -> float:
    """指定したvolumeをtakeする際の取得価格の平均を計算する

    Args:
        orderbook_items (list[OrderbookItem]): orderbookのask or bidのlist
        target_volume (float): 取得するvolume

    Returns:
        float: 取得価格の平均
    """
    total_price = 0.0
    rest_volume = target_volume
    for item in orderbook_items:
        volume = item.volume
        price = item.price

        if rest_volume > volume:
            # 残りのvolumeよりitemのvolumeのほうが小さい場合は、そのまま加重
            total_price += price * volume
            rest_volume -= volume
        else:
            # 残りのvolumeよりitemのvolumeのほうが大きい場合は、残りのvolumeで加重
            total_price += price * rest_volume
            rest_volume = 0

        # rest_volumeが0になったら、加重平均の分母で割る
        if rest_volume == 0:
            total_price /= target_volume
            break
    if total_price == 0.0:
        return np.nan
    return total_price
