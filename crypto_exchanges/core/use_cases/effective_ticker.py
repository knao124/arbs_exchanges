from dataclasses import dataclass
from decimal import Decimal

from arbs_exchanges.core.domain.entities import OrderBookItem
from arbs_exchanges.core.domain.repositories import (
    IExecutionRepository,
    IOrderBookRepository,
)

from .interfaces import ITicker


@dataclass
class _WsEffectiveTickerConfig:
    symbol: str
    target_volume: Decimal


class EffectiveTicker(ITicker):
    def __init__(
        self,
        orderbook_repository: IOrderBookRepository,
        execution_repository: IExecutionRepository,
        symbol: str,
        target_volume: Decimal,
    ):
        self._orderbook_repository = orderbook_repository
        self._execution_repository = execution_repository
        self._config = _WsEffectiveTickerConfig(
            symbol=symbol,
            target_volume=target_volume,
        )

    def _get_bid_ask(self) -> tuple[Decimal, Decimal]:
        target_volume = self._config.target_volume
        orderbook = self._orderbook_repository.fetch_order_book(self._config.symbol)

        bid_price = get_effective_price(orderbook.bid, target_volume)
        ask_price = get_effective_price(orderbook.ask, target_volume)
        return bid_price, ask_price

    def bid_price(self) -> Decimal:
        bid_price, _ = self._get_bid_ask()
        return bid_price

    def ask_price(self) -> Decimal:
        _, ask_price = self._get_bid_ask()
        return ask_price

    def last_price(self) -> Decimal:
        executions = self._execution_repository.fetch_executions(self._config.symbol)
        if len(executions) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return executions[-1].price


def get_effective_price(
    orderbook_items: list[OrderBookItem],
    target_volume: Decimal,
) -> Decimal:
    """指定したvolumeをtakeする際の取得価格の平均を計算する

    Args:
        orderbook_items (list[OrderbookItem]): orderbookのask or bidのlist
        target_volume (float): 取得するvolume

    Returns:
        float: 取得価格の平均
    """
    total_price = Decimal(0.0)
    target_volume = Decimal(target_volume)
    rest_volume = Decimal(target_volume)
    for item in orderbook_items:
        volume = Decimal(item.volume)
        price = Decimal(item.price)

        if rest_volume > volume:
            # 残りのvolumeよりitemのvolumeのほうが小さい場合は、そのまま加重
            total_price += price * volume
            rest_volume -= volume
        else:
            # 残りのvolumeよりitemのvolumeのほうが大きい場合は、残りのvolumeで加重
            total_price += price * rest_volume
            rest_volume = Decimal(0)

        # rest_volumeが0になったら、加重平均の分母で割る
        if rest_volume == Decimal(0):
            total_price /= target_volume
            break

    if total_price == Decimal(0):
        return Decimal("nan")
    return Decimal(total_price)
