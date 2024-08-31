import pytest

from crypto_exchanges.bybit import BybitEquityGetter
from crypto_exchanges.yahoo import YahooFXTicker

from .utils import skip_if_secret_not_set_bybit


class TestBybitEquityGetter:
    @skip_if_secret_not_set_bybit
    def test_testnet_smoke(self):
        # testnetの環境でメソッドを呼び出したときに問題がないことだけテスト
        bb = init_ccxt_exchange(default_type="delivery")
        bb.set_sandbox_mode(True)
        usdjpy_ticker = YahooFXTicker(symbol="JPY=X")
        getter = BybitEquityGetter(
            ccxt_exchange=bb,
            usdjpy_ticker=usdjpy_ticker,
        )
        assert getter.total_in_jpy() >= 0
        assert getter.equity_jpy() >= 0
        assert getter.equity_usd() >= 0

    @pytest.mark.parametrize(
        "val",
        [
            dict(
                usdjpy=100,
                equity_usd=333,
                expected=dict(
                    total_in_jpy=33300,
                    equity_jpy=0,
                    equity_usd=333,
                ),
            ),
        ],
    )
    def test_mocked(self, mocker, val):
        usdjpy_ticker = mocker.MagicMock()
        usdjpy_ticker.last_price.return_value = val["usdjpy"]

        mocked_ccxt = mocker.MagicMock()
        mocked_ccxt.fetch_balance.return_value = dict(
            info=dict(
                result=dict(
                    USDT=dict(
                        equity=str(val["equity_usd"]),
                    ),
                ),
            ),
        )

        getter = BybitEquityGetter(
            ccxt_exchange=mocked_ccxt, usdjpy_ticker=usdjpy_ticker
        )

        assert getter.total_in_jpy() == val["expected"]["total_in_jpy"]
        assert getter.equity_jpy() == val["expected"]["equity_jpy"]
        assert getter.equity_usd() == val["expected"]["equity_usd"]
