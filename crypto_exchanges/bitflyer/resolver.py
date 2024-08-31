"""
bitflyerの各クラスの依存を注入し、initializeするmodule
"""
import os
from dataclasses import dataclass

import ccxt
import pybotters

from ...logger import TickerPriceLogger
from ..oanda.ticker import OANDATicker
from ..yahoo import YahooFXTicker
from .balance import BitflyerBalanceGetter
from .execution import BitflyerWsExecution
from .fee import BitflyerFeeGetter
from .orderer import BitflyerOrderer
from .position import BitflyerSpotRestPositionGetter, BitflyerWsPositionGetter
from .ticker import BitflyerRestTicker, BitFlyerWsEffectiveTicker, BitflyerWsTicker
from .ws import start_bitflyer_ws

try:
    import MetaTrader5 as mt5
except BaseException:
    mt5 = "dummy"


@dataclass
class BitflyerClientSet:
    balance: BitflyerBalanceGetter
    position: BitflyerSpotRestPositionGetter or BitflyerWsPositionGetter
    fee: BitflyerFeeGetter
    orderer: BitflyerOrderer
    ticker: BitflyerWsTicker or BitflyerRestTicker
    effective_ticker: BitFlyerWsEffectiveTicker
    execution: BitflyerWsExecution
    pybotters_client: pybotters.Client
    pybotters_store: pybotters.bitFlyerDataStore
    ccxt_exchange: ccxt.bitflyer


def init_ccxt_exchange() -> ccxt.bitflyer:
    return ccxt.bitflyer(
        {
            "apiKey": os.environ["BITFLYER_API_KEY"],
            "secret": os.environ["BITFLYER_SECRET"],
        }
    )


async def spot_ws_client_set(config: dict) -> BitflyerClientSet:
    symbol = config["bitflyer"]["symbol"]
    is_spot = "FX_" not in symbol
    assert is_spot

    ccxt_exchange = init_ccxt_exchange()

    client, store = await start_bitflyer_ws(
        api_key=os.environ["BITFLYER_API_KEY"],
        secret=os.environ["BITFLYER_SECRET"],
        symbol=symbol,
        verify_ssl=config["bitflyer"]["verify_ssl"],
    )

    balance = BitflyerBalanceGetter(
        ccxt_exchange=ccxt_exchange,
    )
    if symbol == "BTC_JPY":
        position = BitflyerWsPositionGetter(
            store=store,
            symbol=symbol,
            # 初期値は証拠金量と同じ
            initial_value=balance.balance_in_btc(),
        )
    elif symbol == "ETH_JPY":
        position = BitflyerWsPositionGetter(
            store=store,
            symbol=symbol,
            # 初期値は証拠金量と同じ
            initial_value=balance.balance_in_eth(),
        )
    fee_getter = BitflyerFeeGetter(
        ccxt_exchange=ccxt_exchange,
        symbol=symbol,
    )
    orderer = BitflyerOrderer(
        ccxt_exchange=ccxt_exchange,
        fee_getter=fee_getter,
        symbol=symbol,
    )
    ticker = BitflyerWsTicker(
        store=store,
        symbol=symbol,
    )
    effective_ticker = BitFlyerWsEffectiveTicker(
        store=store,
        symbol=symbol,
        amount=config["bitflyer"]["effective_ticker"]["amount"],
    )
    execution = BitflyerWsExecution(
        store=store,
    )

    return BitflyerClientSet(
        balance=balance,
        position=position,
        fee=fee_getter,
        orderer=orderer,
        ticker=ticker,
        effective_ticker=effective_ticker,
        execution=execution,
        pybotters_client=client,
        pybotters_store=store,
        ccxt_exchange=ccxt_exchange,
    )


def spot_rest_client_set(
    symbol: str, ignore_pos_size: float = 0.0
) -> BitflyerClientSet:
    is_spot = "FX_" not in symbol
    assert is_spot

    ccxt_exchange = init_ccxt_exchange()

    balance = BitflyerBalanceGetter(
        ccxt_exchange=ccxt_exchange,
    )
    position = BitflyerSpotRestPositionGetter(
        ccxt_exchange=ccxt_exchange,
        symbol=symbol,
        ignore_value=ignore_pos_size,
    )

    class _TempFeeGetter:
        def taker_fee(self) -> float:
            return 0.20 * 0.01  # 0.20%

    fee_getter = _TempFeeGetter()
    orderer = BitflyerOrderer(
        ccxt_exchange=ccxt_exchange,
        fee_getter=fee_getter,
        symbol=symbol,
    )
    ticker = BitflyerRestTicker(
        ccxt_exchange=ccxt_exchange,
        symbol=symbol,
    )

    return BitflyerClientSet(
        balance=balance,
        position=position,
        fee=None,
        orderer=orderer,
        ticker=ticker,
        effective_ticker=None,
        execution="TODO: 未実装",
        pybotters_client=None,
        pybotters_store=None,
        ccxt_exchange=None,
    )


async def tick_logger(config: dict):
    bitflyer_client_set = await spot_ws_client_set(config)
    coin_ticker = bitflyer_client_set.effective_ticker

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
            "../../../logs/tickers/bitflyer.log",
        ),
        name="bitflyer",
        backupCount=30,
    )
    return logger
