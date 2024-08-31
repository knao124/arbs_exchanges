import time
from logging import getLogger

import ccxt


class ITicker:
    def last_price(self) -> float:
        ...


class BybitEquityGetter:
    def __init__(
        self,
        ccxt_exchange: ccxt.bybit,
        usdjpy_ticker: ITicker,
        update_limit_sec: float = 0.5,
    ):
        self._ccxt_exchange = ccxt_exchange
        self._usdjpy_ticker = usdjpy_ticker
        self._update_limit_sec = update_limit_sec
        self._logger = getLogger(__class__.__name__)

        self._last_ts = 0.0
        self._resp = None

    def total_in_jpy(self) -> float:
        return self.equity_usd() * self._usdjpy_ticker.last_price()

    def equity_jpy(self):
        """
        海外の取引所にJPYは預けない運用のため、JPYのequityは0
        """
        return 0.0

    def equity_usd(self):
        return float(self._balance_resp()["info"]["result"]["USDT"]["equity"])

    def _balance_resp(self):
        """
        ref: https://docs.ccxt.com/en/latest/manual.html?#balance-structure
        ref: https://bybit-exchange.github.io/docs/futuresV2/inverse/#t-balance
        """
        if time.time() - self._last_ts >= self._update_limit_sec:
            self._resp = self._ccxt_exchange.fetch_balance()
            self._last_ts = time.time()

        return self._resp
