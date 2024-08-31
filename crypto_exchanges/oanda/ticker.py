try:
    import MetaTrader5 as MT5
except BaseException:
    MT5 = "dummy"


import time

from . import utils


class OANDATicker:
    def __init__(self, mt5: MT5, symbol: str, update_limit_sec: float):
        self._mt5 = mt5
        self._symbol = symbol
        self._update_limit_sec = update_limit_sec

        self._last_ts = 0.0

        utils.init_symbol(mt5=mt5, symbol=symbol)

    def ask_price(self):
        ask, _ = self._ticker()
        return ask

    def bid_price(self):
        _, bid = self._ticker()
        return bid

    def last_price(self):
        return (self.ask_price() + self.bid_price()) / 2.0

    def _ticker(self):
        if time.time() - self._last_ts >= self._update_limit_sec:
            tick = self._mt5.symbol_info_tick(self._symbol)
            self._last_ask = tick.ask
            self._last_bid = tick.bid
            self._last_ts = time.time()
        return self._last_ask, self._last_bid
