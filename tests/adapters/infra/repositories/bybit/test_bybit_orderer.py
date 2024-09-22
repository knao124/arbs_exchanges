# %%[markdown]

import numpy as np

from crypto_exchanges.adapters.resolvers.bybit import init_bybit_orderer


class TestBybitOrdererPostMarketOrder:
    def test_smoke(self):
        symbol = "BTCUSDT"
        orderer = init_bybit_orderer(symbol=symbol, mode="testnet")
        ret = orderer.post_market_order(side_int=1, size=0.001)
        assert ret["id"] is not None

    def test_size_increased(self):
        symbol = "BTCUSDT"
        orderer = init_bybit_orderer(symbol=symbol, mode="testnet")
        position_getter = init_bybit_position_getter(symbol=symbol, mode="testnet")

        # テスト開始時にポジションがないことを確認
        current_position = position_getter.get_position()
        orderer.post_market_order(
            side_int=np.sign(current_position),
            size=current_position,
        )
        assert position_getter.get_position() == 0.0

        # マーケットオーダーを出してポジションが増えることを確認
        ret = orderer.post_market_order(side_int=1, size=0.001)
        assert position_getter.get_position() == 0.001


class TestBybitOrdererPostLimitOrder:
    def test_post_limit_order(self): ...


def test_bybit_orderer_post_market_order():
    pass


test_bybit_orderer_post_market_order()
