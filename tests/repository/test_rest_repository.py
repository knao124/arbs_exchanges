from dataclasses import asdict
from decimal import Decimal
from typing import Union

import pytest

from crypto_exchanges.adapters.infra.bitflyer.bitflyer_rest_repository import (
    BitflyerRestRepository,
)
from crypto_exchanges.adapters.infra.bybit.bybit_rest_repository import (
    BybitRestRepository,
)
from crypto_exchanges.adapters.resolvers.bitflyer import init_ccxt_bitflyer
from crypto_exchanges.adapters.resolvers.bybit import init_ccxt_bybit
from crypto_exchanges.core.domain.entities import (
    Balance,
    Execution,
    Fee,
    OrderBook,
    Position,
    Symbol,
)
from crypto_exchanges.core.domain.repositories import IRestRepository


@pytest.fixture(
    params=[
        (
            BybitRestRepository,
            init_ccxt_bybit,
            "testnet",
            Symbol.BYBIT_LINEAR_BTCUSDT,
        ),
        (
            BitflyerRestRepository,
            init_ccxt_bitflyer,
            "testnet",
            Symbol.BITFLYER_CFD_BTCJPY,
        ),
    ]
)
def input_values(request) -> tuple[IRestRepository, Symbol]:
    repo_class, init_func, mode, symbol = request.param
    ccxt_exchange = init_func(mode=mode)
    return repo_class(ccxt_exchange, update_interval_sec=1.0), symbol


def test_fetch_order_book(input_values: tuple[IRestRepository, Symbol]):
    repo, symbol = input_values
    order_book = repo.fetch_order_book(symbol)

    assert isinstance(order_book, OrderBook)
    assert len(order_book.bid) > 0
    assert len(order_book.ask) > 0
    assert order_book.bid[0].symbol == symbol
    assert order_book.ask[0].symbol == symbol


def test_fetch_executions(input_values: tuple[IRestRepository, Symbol]):
    repo, symbol = input_values
    executions = repo.fetch_executions(symbol)

    assert isinstance(executions, list)
    assert len(executions) > 0
    assert isinstance(executions[0], Execution)
    assert executions[0].symbol == symbol


def test_fetch_balance(input_values: tuple[IRestRepository, Symbol]):
    repo, _ = input_values
    balance = repo.fetch_balance()

    assert isinstance(balance, Balance)
    print(asdict(balance))
    assert balance.balance_in_btc >= 0
    assert balance.balance_in_usdt >= 0


def test_fetch_fee(input_values: tuple[IRestRepository, Symbol]):
    repo, symbol = input_values
    fee = repo.fetch_fee(symbol)

    assert isinstance(fee, Fee)
    print(asdict(fee))
    assert fee.symbol == symbol
    assert isinstance(fee.maker, Decimal)
    assert isinstance(fee.taker, Decimal)


def test_fetch_positions(input_values: tuple[IRestRepository, Symbol]):
    repo, symbol = input_values
    positions = repo.fetch_positions(symbol)
    print(positions)

    assert isinstance(positions, list)
    for position in positions:
        assert isinstance(position, Position)
        assert position.symbol == symbol
        assert isinstance(position.entry_price, Decimal)
        assert isinstance(position.size_with_sign, Decimal)
        print(asdict(position))
