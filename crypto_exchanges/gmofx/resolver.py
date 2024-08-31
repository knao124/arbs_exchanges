import os

try:
    import MetaTrader5 as mt5
except BaseException:
    mt5 = "dummy"


from ...logger import TickerPriceLogger
from ..oanda import OANDATicker
from ..yahoo import YahooFXTicker
from .ticker import GmoFxRestTicker


def tick_logger(symbol: str, oanda_enabled: bool):
    coin_ticker = GmoFxRestTicker(symbol=symbol)
    if oanda_enabled:
        usdjpy_ticker = OANDATicker(mt5=mt5, symbol="USDJPY", update_limit_sec=0.3)
    else:
        usdjpy_ticker = YahooFXTicker(symbol="JPY=X")

    dirname = os.path.dirname(__file__)

    logger = TickerPriceLogger(
        coin_ticker=coin_ticker,
        usdjpy_ticker=usdjpy_ticker,
        log_filepath=os.path.join(
            dirname,
            "../../../logs/tickers/gmo.log",
        ),
        name="gmo",
        backupCount=30,
    )
    return logger
