import os
import re
from uuid import uuid4

import ccxt
import pytest

from crypto_exchanges import bybit

from .utils import skip_if_secret_not_set_bybit

"""
See the following links to check the min lot size
BTCUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=BTCUSDT
ETHUSDT: https://testnet.bybit.com/data/basic/linear/contract-detail?symbol=ETHUSDT
"""


@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol, settlement_symbol, lot_size",
    [
        ("BTCUSDT", "USDT", 0.0010),
        ("ETHUSDT", "USDT", 0.010),
    ],
)
def test_bybit_orderer_taker(symbol, settlement_symbol, lot_size):
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)

    orderer = bybit.BybitOrderer(
        ccxt_exchange=bb,
        symbol=symbol,
        settlement_symbol=settlement_symbol,
    )
    getter = bybit.BybitRestPositionGetter(
        ccxt_exchange=bb,
        symbol=symbol,
    )

    # long
    pos0 = getter.current_position()
    orderer.post_market_order(side_int=1, size=lot_size)
    pos1 = getter.current_position()

    assert pos0 + lot_size == pytest.approx(pos1)

    # short
    orderer.post_market_order(side_int=-1, size=lot_size)
    pos2 = getter.current_position()

    assert pos1 - lot_size == pytest.approx(pos2)

    # teardown
    if pos2 == pytest.approx(0):
        return
    orderer.post_market_order(side_int=1 if pos2 < 0 else -1, size=abs(pos2))


@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol, settlement_symbol, lot_size",
    [
        ("BTCUSDT", "USDT", 0.0010),
        ("ETHUSDT", "USDT", 0.010),
    ],
)
def test_bybit_orderer_maker(symbol, settlement_symbol, lot_size):
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)

    orderer = bybit.BybitOrderer(
        ccxt_exchange=bb,
        symbol=symbol,
        settlement_symbol=settlement_symbol,
    )
    pos_getter = bybit.BybitRestPositionGetter(
        ccxt_exchange=bb,
        symbol=symbol,
    )

    price_getter = bybit.BybitRestTicker(
        ccxt_exchange=bb, config=bybit.BybitRestTickerConfig(symbol=symbol)
    )

    # ensure all orders are canceled before long/short order starts
    orderer.cancel_all_orders()

    # long/short
    res = orderer.post_limit_order(
        side_int=1, size=lot_size, price=price_getter.bid_price() - 500
    )
    long_order_id = res["id"]
    assert type(long_order_id) is str

    res = orderer.post_limit_order(
        side_int=-1, size=lot_size, price=price_getter.bid_price() + 500
    )
    short_order_id = res["id"]
    assert type(short_order_id) is str

    # cancel
    orderer.cancel_limit_order(order_id=long_order_id)
    orderer.cancel_limit_order(order_id=short_order_id)

    # default post_only
    orderer.post_limit_order(
        side_int=1, size=lot_size, price=price_getter.bid_price() + 500
    )
    assert len(orderer.get_open_orders()) == 0

    # teardown
    pos2 = pos_getter.current_position()
    if pos2 != pytest.approx(0):
        orderer.post_market_order(side_int=1 if pos2 < 0 else -1, size=abs(pos2))

    orderer.cancel_all_orders()


@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol, settlement_symbol, lot_size",
    [
        ("BTCUSDT", "USDT", 0.0010),
        ("ETHUSDT", "USDT", 0.010),
    ],
)
def test_bybit_orderer_cancel_all_orders(symbol, settlement_symbol, lot_size):
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)

    orderer = bybit.BybitOrderer(
        ccxt_exchange=bb,
        symbol=symbol,
        settlement_symbol=settlement_symbol,
    )

    price_getter = bybit.BybitRestTicker(
        ccxt_exchange=bb, config=bybit.BybitRestTickerConfig(symbol=symbol)
    )

    # long/short
    res = orderer.post_limit_order(
        side_int=1, size=lot_size, price=price_getter.bid_price() - 500
    )
    long_order_id = res["id"]
    assert type(long_order_id) is str

    res = orderer.post_limit_order(
        side_int=-1, size=lot_size, price=price_getter.bid_price() + 500
    )
    short_order_id = res["id"]
    assert type(short_order_id) is str

    # 実行
    orderer.cancel_all_orders()

    assert len(orderer.get_open_orders()) == 0


@skip_if_secret_not_set_bybit
@pytest.mark.parametrize(
    "symbol, settlement_symbol, lot_size, order_link_id",
    [
        ("BTCUSDT", "USDT", 0.0010, str(uuid4())),
        ("ETHUSDT", "USDT", 0.010, str(uuid4())),
    ],
)
def test_bybit_orderer_order_client_id(
    mocker, symbol, settlement_symbol, lot_size, order_link_id
):
    bb = ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
        }
    )
    bb.set_sandbox_mode(True)

    generator = mocker.MagicMock()
    generator.generate.return_value = order_link_id

    orderer = bybit.BybitOrderer(
        ccxt_exchange=bb,
        symbol=symbol,
        settlement_symbol=settlement_symbol,
        order_link_id_generator=generator,
    )

    price_getter = bybit.BybitRestTicker(
        ccxt_exchange=bb, config=bybit.BybitRestTickerConfig(symbol=symbol)
    )

    res = orderer.post_limit_order(
        side_int=1, size=lot_size, price=price_getter.bid_price() - 500
    )
    long_order_id = res["id"]

    # order_link_idが設定されているかの確認
    order = None
    ccxt_orders = orderer.get_open_orders()
    for ccxt_order in ccxt_orders:
        if ccxt_order["id"] == long_order_id:
            order = ccxt_order
    assert order is not None
    assert order["info"]["order_link_id"] == order_link_id

    # teardown
    orderer.cancel_all_orders()


@pytest.mark.parametrize(
    "val",
    [
        # 小数3桁に0埋め
        dict(
            uuid4_str="123-" * 9,
            usdjpy_price=100,
            expected="100-000_123-123-123-123-123-123-123-",
        ),
        # 小数3桁まで
        dict(
            uuid4_str="123-" * 9,
            usdjpy_price=100.4444,
            expected="100-444_123-123-123-123-123-123-123-",
        ),
    ],
)
def test_usdjpy_order_link_id_generator_ok(mocker, val):
    usdjpy_ticker = mocker.MagicMock()
    usdjpy_ticker.last_price.return_value = val["usdjpy_price"]
    generator = bybit.USDJPYOrderLinkIdGenerator(usdjpy_ticker=usdjpy_ticker)
    mocker.patch.object(generator, "_generate_uuid4_str", return_value=val["uuid4_str"])
    assert generator.generate() == val["expected"]
    assert len(generator.generate()) == 36


def test_usdjpy_order_link_id_generator_when_raise_internally(mocker):
    usdjpy_ticker = mocker.MagicMock()
    usdjpy_ticker.last_price.side_effect = BaseException()
    generator = bybit.USDJPYOrderLinkIdGenerator(usdjpy_ticker=usdjpy_ticker)

    # 実行
    value = generator.generate()

    # エラーが起きても英数字と-と_で36字が返っているか
    assert re.match(r"(\w|-|_){36}", value) is not None

    # 呼ばれているか
    usdjpy_ticker.last_price.assert_called_once()
