import time
from logging import Logger, getLogger

import ccxt


class CcxtBalanceGetter:
    def __init__(
        self,
        ccxt_exchange: ccxt.Exchange,
        update_limit_sec: float = 0.5,
        logger: Logger = None,
    ):
        self._ccxt_exchange = ccxt_exchange
        self._update_limit_sec = update_limit_sec

        if logger is None:
            logger = getLogger(__class__.__name__)
        self._logger = logger

        self._last_ts = 0.0
        self._resp = None

    def balance_in_btc(self):
        return self._balance_resp()["BTC"]["total"]

    def balance_in_eth(self):
        return self._balance_resp()["ETH"]["total"]

    def balance_in_jpy(self):
        return self._balance_resp()["JPY"]["total"]

    def balance_in_usd(self):
        return self._balance_resp()["USD"]["total"]

    def balance_in_usdt(self):
        return self._balance_resp()["USDT"]["total"]

    def balance_in_usdc(self):
        return self._balance_resp()["USDC"]["total"]

    def _balance_resp(self):
        """
        ref: https://docs.ccxt.com/en/latest/manual.html?#balance-structure
        """
        if time.time() - self._last_ts >= self._update_limit_sec:
            self._resp = self._ccxt_exchange.fetch_balance()
            self._last_ts = time.time()
        return self._resp
