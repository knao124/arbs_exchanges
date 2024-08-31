from logging import getLogger

import ccxt


class PhemexBalanceGetter:
    def __init__(self, ccxt_exchange: ccxt.phemex):
        self._ccxt_exchange = ccxt_exchange
        self._logger = getLogger(__class__.__name__)

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
        # TODO
        return self._ccxt_exchange.fetch_balance(params={"type": "swap", "code": "USD"})
