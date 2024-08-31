"""
bybitの各クラスの依存を注入し、initializeするmodule
"""
import os
from dataclasses import dataclass

import ccxt
import pybotters

from ...logger import TickerPriceLogger
from ..oanda.ticker import OANDATicker
from ..yahoo import YahooFXTicker
from .balance import BybitBalanceGetter
from .execution import BybitWsExecution
from .fee import BybitFeeGetter
from .orderer import BybitOrderer, DefaultOrderLinkIdGenerator
from .position import BybitRestPositionGetter, BybitWsPositionGetter
from .ticker import (
    BybitRestTicker,
    BybitWsEffectiveTicker,
    BybitWsEffectiveTickerConfig,
    BybitWsTicker,
)
from .ws import start_bybit_ws_linear

try:
    import MetaTrader5 as mt5
except BaseException:
    mt5 = "dummy"


@dataclass
class BybitClientSet:
    balance: BybitBalanceGetter
    position: BybitRestPositionGetter or BybitWsPositionGetter
    fee: BybitFeeGetter
    orderer: BybitOrderer
    ticker: BybitWsTicker or BybitRestTicker
    effective_ticker: BybitWsEffectiveTicker
    execution: BybitWsExecution
    pybotters_client: pybotters.Client
    pybotters_store: pybotters.BybitUSDTDataStore
    ccxt_exchange: ccxt.bybit


def init_ccxt_exchange(default_type: str):
    return ccxt.bybit(
        {
            "apiKey": os.environ["BYBIT_API_KEY"],
            "secret": os.environ["BYBIT_SECRET"],
            "options": {"defaultType": default_type},
        }
    )


async def ws_client_set(config: dict, testnet: bool) -> BybitClientSet:
    symbol = config["bybit"]["symbol"]
    ccxt_exchange = init_ccxt_exchange(default_type=config["bybit"]["default_type"])
    ccxt_exchange.set_sandbox_mode(enabled=testnet)

    client, store = await start_bybit_ws_linear(
        api_key=os.environ["BYBIT_API_KEY"],
        secret=os.environ["BYBIT_SECRET"],
        symbol=symbol,
        testnet=testnet,
    )
    balance = BybitBalanceGetter(
        ccxt_exchange=ccxt_exchange,
    )
    position = BybitWsPositionGetter(
        store=store,
        symbol=symbol,
    )
    fee = BybitFeeGetter(
        ccxt_exchange=ccxt_exchange,
        symbol=symbol,
    )
    orderer = BybitOrderer(
        ccxt_exchange=ccxt_exchange,
        symbol=symbol,
        settlement_symbol=config["bybit"]["bybit_orderer"]["settlement_symbol"],
        order_link_id_generator=DefaultOrderLinkIdGenerator(),
    )
    ticker = BybitWsTicker(
        store=store,
        symbol=symbol,
    )

    effective_ticker = BybitWsEffectiveTicker(
        store=store,
        config=BybitWsEffectiveTickerConfig(
            symbol=symbol, amount=config["bybit"]["effective_ticker"]["amount"]
        ),
    )

    execution = BybitWsExecution(
        store=store,
    )
    return BybitClientSet(
        balance=balance,
        position=position,
        fee=fee,
        orderer=orderer,
        ticker=ticker,
        effective_ticker=effective_ticker,
        execution=execution,
        pybotters_client=client,
        pybotters_store=store,
        ccxt_exchange=ccxt_exchange,
    )


async def tick_logger(config: dict, testnet: bool):
    bybit_client_set = await ws_client_set(config, testnet)
    coin_ticker = bybit_client_set.ticker

    if config["oanda"]["enabled"]:  # fakeのとき
        usdjpy_ticker = OANDATicker(mt5=mt5, symbol="USDJPY", update_limit_sec=0.0001)
    else:
        usdjpy_ticker = YahooFXTicker(symbol="JPY=X")

    dirname = os.path.dirname(__file__)

    logger = TickerPriceLogger(
        coin_ticker=coin_ticker,
        usdjpy_ticker=usdjpy_ticker,
        log_filepath=os.path.join(
            dirname,
            "../../../logs/tickers/bybit.log",
        ),
        name="bybit",
        backupCount=30,
    )
    return logger
