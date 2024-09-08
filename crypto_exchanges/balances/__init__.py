from logging import getLogger

import ccxt

from ..common import CcxtBalanceGetter


class BybitBalanceGetter(CcxtBalanceGetter):
    def __init__(self, ccxt_exchange: ccxt.bybit, update_limit_sec: float = 0.5):
        assert type(ccxt_exchange) is ccxt.bybit
        super().__init__(
            ccxt_exchange=ccxt_exchange,
            update_limit_sec=update_limit_sec,
            logger=getLogger(__class__.__name__),
        )

    def balance_in_usd(self):
        return self.balance_in_usdt()

    def balance_in_jpy(self):
        """
        海外の取引所にJPYは預けない運用のため、JPYのbalanceは0
        """
        return 0.0
