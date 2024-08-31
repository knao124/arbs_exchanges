try:
    import MetaTrader5 as MT5
except BaseException:
    MT5 = "dummy"

from logging import getLogger


class OANDAEquityGetter:
    def __init__(self, mt5: MT5):
        self._mt5 = mt5
        self._logger = getLogger(__class__.__name__)

    def total_in_jpy(self) -> float:
        return self.equity_jpy()

    def equity_jpy(self) -> float:
        res = self._balance_resp()
        return res.equity

    def equity_usd(self) -> float:
        return 0.0

    def _balance_resp(self):
        """
        https://www.mql5.com/ja/docs/integration/python_metatrader5/mt5accountinfo_py
        equity = balance + profit
        """
        return self._mt5.account_info()


class ZeroEquityGetter:
    def total_in_jpy(self) -> float:
        return 0.0

    def equity_jpy(self) -> float:
        return 0.0

    def equity_usd(self) -> float:
        return 0.0
