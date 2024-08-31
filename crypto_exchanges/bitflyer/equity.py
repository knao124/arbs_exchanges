from logging import getLogger


class IBalanceGetter:
    def balance_in_btc(self) -> float:
        ...

    def balance_in_eth(self) -> float:
        ...

    def balance_in_jpy(self) -> float:
        ...


class ITicker:
    def last_price(self) -> float:
        ...


class BitflyerEquityGetter:
    # TODO: ethの対応. 今は0としている
    def __init__(
        self,
        balance_getter: IBalanceGetter,
        btcjpy_ticker: ITicker,
        # ethjpy_ticker: ITicker,
    ):
        self._balance_getter = balance_getter
        self._btcjpy_ticker = btcjpy_ticker
        # self._ethjpy_ticker = ethjpy_ticker
        self._logger = getLogger(__class__.__name__)

    def total_in_jpy(self) -> float:
        return self.equity_jpy()

    def equity_jpy(self) -> float:
        """
        _balance_resp()メソッドがbFのccxtにないので、
        「証拠金BTC * BTC/JPYの現在レート + 証拠金ETH * ETH/JPYの現在レート + 証拠金JPY」
        で計算
        """
        pos_btc_jpy = (
            self._balance_getter.balance_in_btc() * self._btcjpy_ticker.last_price()
        )
        # pos_eth_jpy = (
        #     self._balance_getter.balance_in_eth() * self._ethjpy_ticker.last_price()
        # )
        pos_eth_jpy = 0.0
        balance_jpy = self._balance_getter.balance_in_jpy()
        return pos_btc_jpy + pos_eth_jpy + balance_jpy

    def equity_usd(self) -> float:
        """
        国内の取引所にUSDは預けない運用のため、USDのequityは0
        """
        return 0.0
