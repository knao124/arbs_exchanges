from logging import getLogger

import ccxt

from ..common import CcxtBalanceGetter


class BitflyerBalanceGetter(CcxtBalanceGetter):
    def __init__(self, ccxt_exchange: ccxt.bitflyer, update_limit_sec: float = 0.5):
        assert type(ccxt_exchange) is ccxt.bitflyer
        logger = getLogger(__class__.__name__)

        super().__init__(ccxt_exchange=ccxt_exchange, logger=logger)

    def balance_in_usd(self):
        """
        国内の取引所にUSDは預けない運用のため、USDのequityは0
        """
        return 0.0
