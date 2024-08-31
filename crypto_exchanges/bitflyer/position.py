from logging import getLogger

import ccxt
import pybotters

from ..common import CcxtRestPositionGetter


class BitflyerRestPositionGetter(CcxtRestPositionGetter):
    def __init__(self, ccxt_exchange: ccxt.Exchange, symbol: str, position_type: type):
        assert type(ccxt_exchange) is ccxt.bitflyer
        assert "FX" in symbol

        super().__init__(
            ccxt_exchange=ccxt_exchange,
            symbol=symbol,
            position_type=position_type,
            logger=getLogger(__class__.__name__),
        )


class BitflyerSpotRestPositionGetter:
    """
    - https://docs.ccxt.com/en/latest/manual.html#position-structure

    現物のみなのでbalanceの表示
    symbol: BTC or ETH or JPY
    最初のバランスを記録しておき、その値からの差分を表示する
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.bitflyer,
        symbol: str,
        ignore_value: float,
    ):
        assert type(ccxt_exchange) is ccxt.bitflyer
        self._ccxt_exchange = ccxt_exchange
        # monkeypatch: balanceのsymbolに合わせる
        if symbol == "BTC_JPY":
            symbol = "BTC"
        elif symbol == "ETH_JPY":
            symbol = "ETH"
        else:
            raise ValueError(f"{symbol=} not supported")
        self._symbol = symbol

        self._ignore_value = ignore_value

    def current_position(self) -> int:
        balance = self._ccxt_exchange.fetch_balance()
        pos = balance[self._symbol]["free"]
        # 無視する分を除いて返却
        return pos - self._ignore_value

    def avg_price(self):
        return 0


class BitflyerWsPositionGetter:
    def __init__(
        self,
        store: pybotters.bitFlyerDataStore,
        symbol: str,
        initial_value: float,
    ):

        self._store = store
        self._symbol = symbol

        self._initial_value = initial_value

        self._logger = getLogger(__class__.__name__)

    def current_position(self) -> float or int:
        positions = self._store.positions.find()

        self._logger.debug(f"{positions=}, {self._initial_value=}")

        pos = 0
        for pos_dict in positions:
            side_int = 1 if pos_dict["side"] == "BUY" else -1
            size_with_sign = float(pos_dict["size"]) * side_int
            # NOTE: pybottersの実装が間違っているので以下だとバグる
            #       MyBitflyerDataStoreを実装したので、それに合わせてこちらも実装を変えている
            # commission = pos_dict["commission"]
            # sfd = pos_dict["sfd"]
            # pos += size_with_sign - commission - sfd
            pos += size_with_sign

        return pos + self._initial_value

    def avg_price(self):
        return 0
