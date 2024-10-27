from dataclasses import dataclass
from decimal import Decimal

from arbs_exchanges.core.domain.repositories import (
    IExecutionRepository,
    IOrderBookRepository,
)

from .interfaces import ITicker


@dataclass
class _TickerConfig:
    symbol: str


class Ticker(ITicker):
    def __init__(
        self,
        orderbook_repository: IOrderBookRepository,
        execution_repository: IExecutionRepository,
        symbol: str,
    ):
        self._orderbook_repository = orderbook_repository
        self._execution_repository = execution_repository
        self._config = _TickerConfig(symbol=symbol)

    def bid_price(self) -> Decimal:
        order_book = self._orderbook_repository.fetch_order_book(self._config.symbol)

        if len(order_book.bid) == 0:
            return Decimal("nan")
        return Decimal(order_book.bid[0].price)

    def ask_price(self) -> Decimal:
        order_book = self._orderbook_repository.fetch_order_book(self._config.symbol)

        if len(order_book.ask) == 0:
            return Decimal("nan")
        return Decimal(order_book.ask[0].price)

    def last_price(self) -> Decimal:
        trades = self._execution_repository.fetch_executions(self._config.symbol)

        # 履歴がない場合はask bidの中央を返す
        if len(trades) == 0:
            return (self.bid_price() + self.ask_price()) * 0.5
        return Decimal(trades[-1].price)
