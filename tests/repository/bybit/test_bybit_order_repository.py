from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from crypto_exchanges.adapters.infra.bybit import (
    BybitDefaultOrderLinkIdGenerator,
    BybitOrderRepository,
    BybitRestRepository,
)
from crypto_exchanges.adapters.resolvers.bybit import init_ccxt_bybit
from crypto_exchanges.core.domain.entities import Order, OrderType, Symbol


@pytest.fixture
def bybit_order_repo():
    ccxt_bybit = init_ccxt_bybit(mode="testnet")
    generator = BybitDefaultOrderLinkIdGenerator()
    return BybitOrderRepository(ccxt_bybit, generator, Symbol("BTC/USDT:USDT"))


@pytest.fixture
def bybit_repo() -> BybitRestRepository:
    ccxt_bybit = init_ccxt_bybit(mode="testnet")
    return BybitRestRepository(ccxt_bybit, 1.0)


def clear_all(
    bybit_repo: BybitRestRepository, order_repo: BybitOrderRepository, symbol: Symbol
):
    # 注文を全てキャンセルする
    order_repo.remove_all_orders()

    # ポジションを0にする
    positions = bybit_repo.fetch_positions(symbol)
    position_all = Decimal(0)
    for position in positions:
        position_all += position.size_with_sign
    if position_all != 0:
        order_repo.create_market_order(position_all * -1)


@pytest.mark.parametrize("order_size_with_sign", [Decimal("0.01"), Decimal("-0.01")])
def test_create_market_order(
    bybit_order_repo: BybitOrderRepository,
    bybit_repo: BybitRestRepository,
    order_size_with_sign: Decimal,
):
    """成行注文が無事に作成できているかのテスト"""

    symbol = Symbol("BTC/USDT:USDT")
    size_with_sign = order_size_with_sign

    order = bybit_order_repo.create_market_order(size_with_sign)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.MARKET
    assert order.order_id is not None and order.order_id != ""
    assert order.symbol == symbol
    assert order.size_with_sign == size_with_sign
    assert order.price.is_nan()

    # ポジションが想定どおり増えていることを確認
    positions = bybit_repo.fetch_positions(symbol)
    position_all = sum(position.size_with_sign for position in positions)
    assert position_all == size_with_sign

    clear_all(bybit_repo, bybit_order_repo, symbol)


def test_create_and_remove_limit_order(
    bybit_order_repo: BybitOrderRepository, bybit_repo: BybitRestRepository
):
    """指値注文が無事に作成できているか, キャンセルできているかのテスト"""

    symbol = Symbol("BTC/USDT:USDT")
    size_with_sign = Decimal("0.01")
    price = Decimal("50000")
    post_only = True

    # 1-a. 注文を作成する
    order = bybit_order_repo.create_limit_order(size_with_sign, price, post_only)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.LIMIT
    assert order.order_id is not None and order.order_id != ""
    assert order.symbol == symbol
    assert order.size_with_sign == size_with_sign
    assert order.price == price

    # 1-b. 想定どおりOpen Orderが増えていることを確認
    open_orders = bybit_order_repo.get_open_orders()
    assert len(open_orders) >= 1

    # 2-a. 注文をキャンセルする
    bybit_order_repo.remove_order(order_id=order.order_id)

    # 2-b. 注文がキャンセルされていることを確認
    open_orders = bybit_order_repo.get_open_orders()
    assert len(open_orders) == 0


def test_remove_all_orders(
    bybit_order_repo: BybitOrderRepository, bybit_repo: BybitRestRepository
):
    """全ての注文をキャンセルするテスト"""

    size_with_sign = Decimal("0.01")
    price = Decimal("50000")
    post_only = True

    # 1. 注文を作成する
    _ = bybit_order_repo.create_limit_order(
        size_with_sign=size_with_sign,
        price=price,
        post_only=post_only,
    )

    # 2. 注文をキャンセルする
    bybit_order_repo.remove_all_orders()

    # 3. 注文がキャンセルされていることを確認
    open_orders = bybit_order_repo.get_open_orders()
    assert len(open_orders) == 0


def test_update_order(
    bybit_order_repo: BybitOrderRepository, bybit_repo: BybitRestRepository
):
    """注文を編集するテスト"""

    symbol = Symbol("BTC/USDT:USDT")
    size_with_sign = Decimal("0.01")
    price = Decimal("50000")
    post_only = True

    # 1. 注文を作成する
    order = bybit_order_repo.create_limit_order(size_with_sign, price, post_only)

    # 2. 注文を編集する
    new_size_with_sign = Decimal("0.02")
    new_price = Decimal("50000")
    updated_order = bybit_order_repo.update_order(
        order.order_id, new_size_with_sign, new_price
    )

    # 3. 注文が編集されていることを確認
    assert isinstance(updated_order, Order)
    assert updated_order.order_id == order.order_id
    assert updated_order.symbol == symbol
    assert updated_order.size_with_sign == new_size_with_sign
    assert updated_order.price == new_price


def test_get_latest_orders(
    bybit_order_repo: BybitOrderRepository, bybit_repo: BybitRestRepository
):
    """注文を取得するテスト"""

    # 1. 注文を作成する
    bybit_order_repo.create_limit_order(
        size_with_sign=Decimal("0.01"),
        price=Decimal("50000"),
        post_only=True,
    )

    # 2. 注文をキャンセルする
    bybit_order_repo.remove_all_orders()

    # 3. 注文を取得する
    orders = bybit_order_repo.get_latest_orders()
    assert len(orders) > 0
