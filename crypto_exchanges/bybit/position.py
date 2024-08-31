import ccxt
import pybotters


class BybitRestPositionGetter:
    """
    - https://github.com/ccxt/ccxt/blob/master/python/ccxt/bybit.py
    - https://docs.ccxt.com/en/latest/manual.html#position-structure
    """

    def __init__(self, ccxt_exchange: ccxt.bybit, symbol: str):
        self._bybit = ccxt_exchange
        self._symbol = symbol

        self._position_type = _position_type(symbol)

    def current_position(self) -> int:
        positions = self._bybit.fetch_positions(symbols=[self._symbol])
        if len(positions) == 0:
            return 0

        total = 0.0
        for pos in positions:
            base_size = pos["contracts"]
            if base_size is None:
                continue
            side_sign = 1 if pos["side"] == "long" else -1
            total += base_size * side_sign
        return self._position_type(total)

    def avg_price(self) -> float or None:
        positions = self._bybit.fetch_positions(symbols=[self._symbol])
        if len(positions) == 0:
            return
        if len(positions) > 1:
            raise BaseException(f"想定外, {positions=}")
        return positions[0]["entryPrice"]


class BybitWsPositionGetter:
    def __init__(
        self,
        store: pybotters.BybitDataStore or pybotters.BybitDataStore,
        symbol: str,
    ):

        self._store = store
        self._symbol = symbol
        self._position_type = _position_type(symbol)

        self._current_position = 0

    def current_position(self) -> float or int:
        pos_dict = self._store.position.one(self._symbol)

        if pos_dict is None or pos_dict["side"] is None:
            pos = 0.0
        else:
            side_int = 1 if pos_dict["side"] == "Buy" else -1
            size_with_sign = float(pos_dict["size"]) * side_int
            pos = size_with_sign

        return self._position_type(pos)

    def avg_price(self) -> float or None:
        """
        ポジションの平均取得単価を返す

        Returns:
            float or None: ポジションをもっていない場合はNoneが返る
        """
        pos_dict = self._store.position.one(self._symbol)
        if pos_dict is None or pos_dict["entry_price"] == 0:
            price = None
        else:
            price = float(pos_dict["entry_price"])
        return price


def _position_type(symbol: str):
    # linear or spot (Coin)
    if "USDT" in symbol:
        return float

    # inverse (USD)
    return int
