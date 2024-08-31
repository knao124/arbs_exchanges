from logging import Logger, getLogger

import ccxt
import numpy as np


class CcxtRestPositionGetter:
    """
    - https://docs.ccxt.com/en/latest/manual.html#position-structure
    """

    def __init__(
        self,
        ccxt_exchange: ccxt.Exchange,
        symbol: str,
        position_type: type,
        logger: Logger = None,
    ):
        self._ccxt_exchange = ccxt_exchange
        self._symbol = symbol
        self._position_type = position_type

        if logger is None:
            logger = getLogger(__class__.__name__)
        self._logger = logger

    def current_position(self) -> float or int:
        positions = self._ccxt_exchange.fetch_positions(symbols=[self._symbol])
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

    def avg_price(self) -> float:
        positions = self._ccxt_exchange.fetch_positions(symbols=[self._symbol])
        if len(positions) == 0:
            return np.nan
        total_value = 0.0
        total_size = 0.0
        for pos in positions:
            base_size = pos["contracts"]
            if base_size is None:
                continue
            side_sign = 1 if pos["side"] == "long" else -1

            total_value += pos["entryPrice"] * base_size * side_sign
            total_size += base_size * side_sign
        avg_price = total_value / total_size
        return self._position_type(avg_price)
