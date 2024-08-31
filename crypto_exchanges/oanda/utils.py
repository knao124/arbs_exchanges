try:
    import MetaTrader5
except BaseException:
    MetaTrader5 = "dummy"


from logging import getLogger

logger = getLogger(__name__)


def init_and_login(mt5: MetaTrader5, userid: str, password: str):
    if not mt5.initialize():
        logger.error(
            f"Failed mt5.initialize(). error code={mt5.last_error()}",
        )
        raise

    if not mt5.login(int(userid), password=password):
        logger.error(f"Failed mt5.login(). error code={mt5.last_error()}")
        raise


def init_symbol(mt5: MetaTrader5, symbol: str):
    # 買いリクエスト構造体を準備する
    # symbol = "USDJPY"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        raise

    # 銘柄が「気配値表示」にない場合は追加する
    if not symbol_info.visible:
        logger.info(f"{symbol} is not visible. trying to switch on")

        if not mt5.symbol_select(symbol, True):
            logger.error(f"mt5.symbol_select('{symbol}') failed, exit")
            mt5.shutdown()
            raise
