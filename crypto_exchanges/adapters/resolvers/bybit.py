import os
from dataclasses import dataclass
from typing import Literal

import ccxt

from arbs_exchanges.adapters.infra.bybit.bybit_order_link_id_generator import (
    BybitDefaultOrderLinkIdGenerator,
)
from arbs_exchanges.adapters.infra.bybit.bybit_order_repository import (
    BybitOrderRepository,
)
from arbs_exchanges.adapters.infra.bybit.bybit_rest_repository import (
    BybitRestRepository,
)
from arbs_exchanges.adapters.infra.bybit.bybit_sizer import init_sizer
from arbs_exchanges.core.use_cases import (
    BalanceGetter,
    EffectiveTicker,
    EquityGetter,
    FeeGetter,
    Orderer,
    PositionGetter,
    Ticker,
)


def init_ccxt_bybit(
    mode: Literal["testnet", "real"],
    default_type: str = "future",
) -> ccxt.bybit:
    """bybitのccxt exchangeを返す

    Args:
        default_type (str): デフォルトの取引タイプ. future or spot

    Returns:
        ccxt.bybit: bybitのccxt exchange
    """
    if mode == "testnet":
        ccxt_bybit = ccxt.bybit(
            {
                "apiKey": os.environ["BYBIT_API_KEY_TESTNET"],
                "secret": os.environ["BYBIT_SECRET_TESTNET"],
                "options": {"defaultType": default_type},
            }
        )
        ccxt_bybit.set_sandbox_mode(True)
        return ccxt_bybit
    elif mode == "real":
        return ccxt.bybit(
            {
                "apiKey": os.environ["BYBIT_API_KEY"],
                "secret": os.environ["BYBIT_SECRET"],
                "options": {"defaultType": default_type},
            }
        )


@dataclass
class Exchange:
    balance_getter: BalanceGetter
    effective_ticker: EffectiveTicker
    equity_getter: EquityGetter
    fee_getter: FeeGetter
    position_getter: PositionGetter
    ticker: Ticker
    orderer: Orderer


def init_bybit_exchange(symbol: str, mode: Literal["testnet", "real"]) -> Exchange:
    # repo
    bybit_ccxt = init_ccxt_bybit(mode=mode)
    repo = BybitRestRepository(
        ccxt_exchange=bybit_ccxt,
        update_interval_sec=0.1,
    )  # TODO: update_interval_sec

    # ticker
    ticker = Ticker(
        orderbook_repository=repo,
        execution_repository=repo,
        symbol=symbol,
    )

    # effective_ticker
    effective_ticker = EffectiveTicker(
        orderbook_repository=repo,
        execution_repository=repo,
        symbol=symbol,
        target_volume=0.01,
    )

    # balance
    balance_getter = BalanceGetter(repository=repo)

    # equity_getter
    equity_getter = EquityGetter(repository=repo, usdjpy_ticker=ticker)

    # fee_getter
    fee_getter = FeeGetter(repository=repo)

    # position_getter
    position_getter = PositionGetter(repository=repo, symbol=symbol)

    # orderer
    order_repo = BybitOrderRepository(
        ccxt_exchange=bybit_ccxt,
        order_link_id_generator=BybitDefaultOrderLinkIdGenerator(),
    )
    orderer = Orderer(
        repository=order_repo,
        sizer=init_sizer(symbol=symbol),
        symbol=symbol,
    )

    return Exchange(
        balance_getter=balance_getter,
        effective_ticker=effective_ticker,
        equity_getter=equity_getter,
        fee_getter=fee_getter,
        position_getter=position_getter,
        ticker=ticker,
        orderer=orderer,
    )
