from decimal import Decimal

import pytest

from crypto_exchanges.adapters.infra.bitflyer import (
    BitflyerOrderRepository,
    BitflyerRestRepository,
)
from crypto_exchanges.adapters.infra.bybit import (
    BybitDefaultOrderLinkIdGenerator,
    BybitOrderRepository,
    BybitRestRepository,
)
from crypto_exchanges.adapters.infra.phemex import (
    PhemexOrderRepository,
    PhemexRestRepository,
)
from crypto_exchanges.adapters.resolvers.bitflyer import init_ccxt_bitflyer
from crypto_exchanges.adapters.resolvers.bybit import init_ccxt_bybit
from crypto_exchanges.adapters.resolvers.phemex import init_ccxt_phemex
from crypto_exchanges.core.domain.entities import Order, OrderType, Symbol
from crypto_exchanges.core.domain.repositories import IOrderRepository, IRestRepository


@pytest.fixture(
    params=[
        (
           BybitOrderRepository,
           BybitRestRepository,
           init_ccxt_bybit,
           "testnet",
           Symbol("BTC/USDT:USDT"),
        ),
        (
           BitflyerOrderRepository,
           BitflyerRestRepository,
           init_ccxt_bitflyer,
           "testnet",
           Symbol.BITFLYER_CFD_BTCJPY,
        ),
        (
            PhemexOrderRepository,
            PhemexRestRepository,
            init_ccxt_phemex,
            "testnet",
            Symbol.PHEMEX_LINEAR_BTCUSDT,
        ),
    ]
)
def order_repo_and_rest_repo(
    request,
) -> tuple[IOrderRepository, IRestRepository, Symbol]:
    order_repo_class, rest_repo_class, init_func, mode, symbol = request.param
    ccxt_exchange = init_func(mode=mode)

    if order_repo_class == BybitOrderRepository:
        generator = BybitDefaultOrderLinkIdGenerator()
        order_repo = order_repo_class(ccxt_exchange, generator, symbol)
    else:
        order_repo = order_repo_class(ccxt_exchange, symbol)

    rest_repo = rest_repo_class(ccxt_exchange, update_interval_sec=1.0)
    return order_repo, rest_repo, symbol


def clear_all(rest_repo: IRestRepository, order_repo: IOrderRepository, symbol: Symbol):
    # 注文を全てキャンセルする
    order_repo.remove_all_orders()

    # ポジションを0にする
    positions = rest_repo.fetch_positions(symbol)
    position_all = Decimal(0)
    for position in positions:
        position_all += position.size_with_sign
    if position_all != 0:
        order_repo.create_market_order(position_all * -1)


@pytest.mark.parametrize("order_size_with_sign", [Decimal("0.01"), Decimal("-0.01")])
def test_create_market_order(
    order_repo_and_rest_repo: tuple[IOrderRepository, IRestRepository, Symbol],
    order_size_with_sign: Decimal,
):
    """成行注文が無事に作成できているかのテスト"""
    order_repo, rest_repo, symbol = order_repo_and_rest_repo
    size_with_sign = order_size_with_sign

    clear_all(rest_repo, order_repo, symbol)

    order = order_repo.create_market_order(size_with_sign)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.MARKET
    assert order.order_id is not None and order.order_id != ""
    assert order.symbol == symbol
    assert order.size_with_sign == size_with_sign
    assert order.price.is_nan() or order.price > 0

    # ポジションが想定どおり増えていることを確認
    positions = rest_repo.fetch_positions(symbol)
    position_all = sum(position.size_with_sign for position in positions)
    assert position_all == size_with_sign

    clear_all(rest_repo, order_repo, symbol)


def test_create_and_remove_limit_order(
    order_repo_and_rest_repo: tuple[IOrderRepository, IRestRepository, Symbol]
):
    """指値注文が無事に作成できているか, キャンセルできているかのテスト"""
    order_repo, rest_repo, symbol = order_repo_and_rest_repo
    size_with_sign = Decimal("0.01")
    if symbol.is_base_jpy:
        price = Decimal("8800000")
    elif symbol.is_base_usd:
        price = Decimal("50000")
    else:
        raise ValueError(f"Unsupported symbol: {symbol}")
    post_only = False

    # 1-a. 注文を作成する
    order = order_repo.create_limit_order(size_with_sign, price, post_only)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.LIMIT
    assert order.order_id is not None and order.order_id != ""
    assert order.symbol == symbol
    assert order.size_with_sign == size_with_sign
    assert order.price == price

    # 1-b. 想定どおりOpen Orderが増えていることを確認
    open_orders = order_repo.get_open_orders()
    assert len(open_orders) >= 1

    # 2-a. 注文をキャンセルする
    order_repo.remove_order(order_id=order.order_id)

    # 2-b. 注文がキャンセルされていることを確認
    open_orders = order_repo.get_open_orders()
    assert len(open_orders) == 0


def test_remove_all_orders(
    order_repo_and_rest_repo: tuple[IOrderRepository, IRestRepository, Symbol]
):
    """全ての注文をキャンセルするテスト"""
    order_repo, rest_repo, symbol = order_repo_and_rest_repo
    size_with_sign = Decimal("0.01")
    if symbol.is_base_jpy:
        price = Decimal("8800000")
    elif symbol.is_base_usd:
        price = Decimal("50000")
    else:
        raise ValueError(f"Unsupported symbol: {symbol}")
    post_only = False

    # 1. 注文を作成する
    _ = order_repo.create_limit_order(
        size_with_sign=size_with_sign,
        price=price,
        post_only=post_only,
    )

    # 2. 注文をキャンセルする
    order_repo.remove_all_orders()

    # 3. 注文がキャンセルされていることを確認
    open_orders = order_repo.get_open_orders()
    assert len(open_orders) == 0


def test_update_order(
    order_repo_and_rest_repo: tuple[IOrderRepository, IRestRepository, Symbol]
):
    """注文を編集するテスト"""
    order_repo, rest_repo, symbol = order_repo_and_rest_repo
    size_with_sign = Decimal("0.01")
    if symbol.is_base_jpy:
        price = Decimal("8800000")
    elif symbol.is_base_usd:
        price = Decimal("50000")
    else:
        raise ValueError(f"Unsupported symbol: {symbol}")

    post_only = False

    # 1. 注文を作成する
    order = order_repo.create_limit_order(size_with_sign, price, post_only)

    # 2. 注文を編集する
    new_size_with_sign = Decimal("0.012")
    new_price = price
    updated_order = order_repo.update_order(
        order.order_id, new_size_with_sign, new_price
    )

    # 3. 注文が編集されていることを確認
    assert isinstance(updated_order, Order)
    assert updated_order.symbol == symbol
    assert updated_order.size_with_sign == new_size_with_sign
    assert updated_order.price == new_price

    clear_all(rest_repo, order_repo, symbol)


def test_get_latest_orders(
    order_repo_and_rest_repo: tuple[IOrderRepository, IRestRepository, Symbol]
):
    """注文を取得するテスト"""
    order_repo, rest_repo, symbol = order_repo_and_rest_repo

    if symbol.is_base_jpy:
        price = Decimal("8800000")
    elif symbol.is_base_usd:
        price = Decimal("50000")
    else:
        raise ValueError(f"Unsupported symbol: {symbol}")

    # 1. 注文を作成する
    order_repo.create_limit_order(
        size_with_sign=Decimal("0.01"),
        price=price,
        post_only=False,
    )

    # 2. 注文をキャンセルする
    order_repo.remove_all_orders()

    # 3. 注文を取得する
    orders = order_repo.get_latest_orders()
    assert len(orders) > 0
