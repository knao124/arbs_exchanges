try:
    import MetaTrader5 as MT5
except BaseException:
    MT5 = "dummy"

from logging import getLogger


class OANDABalanceGetter:
    def __init__(self, mt5: MT5):
        self._mt5 = mt5
        self._logger = getLogger(__class__.__name__)

    def balance_in_jpy(self):
        res = self._balance_resp()
        return res.balance

    def balance_in_usd(self):
        return 0.0

    def balance_in_btc(self):
        return 0.0

    def _balance_resp(self):
        """
        https://www.mql5.com/ja/docs/integration/python_metatrader5/mt5accountinfo_py
        equity = balance + profit
        """
        return self._mt5.account_info()
