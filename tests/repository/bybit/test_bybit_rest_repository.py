from dataclasses import asdict
from decimal import Decimal

import pytest

from crypto_exchanges.adapters.infra.bybit.bybit_rest_repository import (
    BybitRestRepository,
)
from crypto_exchanges.adapters.resolvers.bybit import init_ccxt_bybit
from crypto_exchanges.core.domain.entities import (
    Balance,
    Execution,
    Fee,
    OrderBook,
    Position,
)


@pytest.fixture
def bybit_repo() -> BybitRestRepository:
    ccxt_bybit = init_ccxt_bybit(mode="testnet")
    return BybitRestRepository(ccxt_bybit, update_interval_sec=1.0)


def test_fetch_order_book(bybit_repo: BybitRestRepository):
    symbol = "BTC/USDT"
    order_book = bybit_repo.fetch_order_book(symbol)

    assert isinstance(order_book, OrderBook)
    assert len(order_book.bid) > 0
    assert len(order_book.ask) > 0
    assert order_book.bid[0].symbol == symbol
    assert order_book.ask[0].symbol == symbol


def test_fetch_executions(bybit_repo: BybitRestRepository):
    symbol = "BTC/USDT"
    executions = bybit_repo.fetch_executions(symbol)

    assert isinstance(executions, list)
    assert len(executions) > 0
    assert isinstance(executions[0], Execution)
    assert executions[0].symbol == symbol


def test_fetch_balance(bybit_repo: BybitRestRepository):
    balance = bybit_repo.fetch_balance()

    assert isinstance(balance, Balance)
    print(asdict(balance))
    assert balance.balance_in_btc >= 0
    assert balance.balance_in_usdt >= 0


def test_fetch_fee(bybit_repo: BybitRestRepository):
    symbol = "BTC/USDT"
    fee = bybit_repo.fetch_fee(symbol)

    assert isinstance(fee, Fee)
    print(asdict(fee))
    assert fee.symbol == symbol
    assert isinstance(fee.maker, Decimal)
    assert isinstance(fee.taker, Decimal)


def test_fetch_positions(bybit_repo: BybitRestRepository):
    symbol = "BTC/USDT"
    positions = bybit_repo.fetch_positions(symbol)
    print(positions)

    assert isinstance(positions, list)
    for position in positions:
        assert isinstance(position, Position)
        assert position.symbol == symbol
        assert position.side_int in [-1, 1]
        assert isinstance(position.entry_price, Decimal)
        assert isinstance(position.size, Decimal)
        print(asdict(position))
