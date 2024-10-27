from decimal import Decimal

from arbs_exchanges.core.domain.entities import (
    Balance,
    OrderBook,
    OrderBookItem,
    Position,
    Symbol,
)
from arbs_exchanges.core.domain.repositories import (
    IBalanceRepository,
    IExecutionRepository,
    IOrderBookRepository,
    IPositionRepository,
)

from .mt5_interface import MetaTrader5Interface


class OandaRestRepository(
    IOrderBookRepository,
    IPositionRepository,
    IBalanceRepository,
):
    def __init__(self, mt5: MetaTrader5Interface, magic: int):
        self._mt5 = mt5
        self._magic = magic

    def fetch_order_book(self, symbol: Symbol) -> OrderBook:
        """OrderBookを返す. tickから擬似的に生成する

        Args:
            symbol (Symbol): 通貨ペア

        Returns:
            OrderBook: orderbook
        """
        tick = self._mt5.symbol_info_tick(symbol.value)
        return OrderBook(
            ask=[
                OrderBookItem(
                    symbol=symbol.value,
                    side_int=-1,
                    price=Decimal(str(tick.ask)),
                    volume=Decimal("inf"),
                )
            ],
            bid=[
                OrderBookItem(
                    symbol=symbol.value,
                    side_int=1,
                    price=Decimal(str(tick.bid)),
                    volume=Decimal("inf"),
                )
            ],
        )

    def fetch_balance(self) -> Balance:
        """_summary_

        Returns:
            Balance: 残高
        """
        account_info = self._mt5.account_info()
        return Balance(
            balance_in_btc=Decimal(0),
            balance_in_eth=Decimal(0),
            balance_in_jpy=Decimal(account_info.balance),
            balance_in_usd=Decimal(0),
            balance_in_usdt=Decimal(0),
            balance_in_usdc=Decimal(0),
        )

    def fetch_positions(self, symbol: Symbol) -> list[Position]:
        """
        https://www.mql5.com/ja/docs/integration/python_metatrader5/mt5positionsget_py

        TradePosition(
            ticket=4098461,
            time=1667386683,
            time_msc=1667386683719,
            time_update=1667386683,
            time_update_msc=1667386683719,
            type=1,
            magic=12345678,
            identifier=4098461,
            reason=3,
            volume=0.2,
            price_open=147.321,
            sl=0.0,
            tp=0.0,
            price_current=147.721,
            swap=-350.0,
            profit=-8000.0,
            symbol="USDJPY",
            comment="python script op",
            external_id="",
        )
        """
        mt5_positions = self._mt5.positions_get(symbol=symbol.value)
        positions = []
        for mt5_position in mt5_positions:
            if mt5_position.magic != self._magic:
                continue
            if mt5_position.type == 1:
                side_int = 1
            else:
                side_int = -1
            size_with_sign = Decimal(mt5_position.volume * 100_000) * side_int
            position = Position(
                id=str(mt5_position.ticket),
                symbol=symbol.value,
                entry_price=Decimal(mt5_position.price_open),
                size_with_sign=size_with_sign,
            )
            positions.append(position)
        return positions
