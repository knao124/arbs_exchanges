import MetaTrader5
from crypto_exchanges.adapters.infra.oanda import OandaRestRepository
from crypto_exchanges.core.domain.entities import Symbol
from crypto_exchanges.adapters.infra.oanda import OandaOrderRepository
from decimal import Decimal


def test_oanda_smoke():
    MetaTrader5.initialize()
    repo = OandaRestRepository(
        mt5=MetaTrader5,
        magic=12345678,
    )
    symbol = Symbol.OANDA_USDJPY
    repo.fetch_balance()
    repo.fetch_order_book(symbol=symbol)
    repo.fetch_positions(symbol=symbol)

    orderer = OandaOrderRepository(
        mt5=MetaTrader5,
        position_repo=repo,
        symbol=Symbol.OANDA_USDJPY,
        magic=12345678,
        spread_max_limit=1,
    )
    orderer.create_market_order(Decimal("100000"))
    positions = repo.fetch_positions(symbol=symbol)
    assert len(positions) > 0

    orderer.create_market_order(Decimal("-100000"))
    positions = repo.fetch_positions(symbol=symbol)
    assert len(positions) == 0
