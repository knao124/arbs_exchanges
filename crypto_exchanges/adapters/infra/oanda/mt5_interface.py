from dataclasses import dataclass


@dataclass
class Mt5Tick:
    bid: float
    ask: float


@dataclass
class Mt5AccountInfo:
    balance: float
    equity: float


@dataclass
class Mt5Position:
    ticket: int
    type: int
    magic: int
    volume: float
    price_open: float
    symbol: str


@dataclass
class Mt5OrderSendResult:
    # https://www.mql5.com/ja/docs/constants/structures/mqltraderesult
    retcode: int
    deal: int
    order: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    retcode_external: int


@dataclass
class Mt5OrderCheckResult:
    # https://www.mql5.com/ja/docs/constants/structures/mqltradecheckresult
    retcode: int
    balance: float
    equity: float
    profit: float
    margin: float
    margin_free: float
    margin_level: float
    comment: str


class MetaTrader5Interface:
    """Macだと pip installできないので、 インターフェースのみ、自前で定義する"""

    def symbol_info_tick(self, symbol: str) -> Mt5Tick: ...

    def account_info(self) -> Mt5AccountInfo: ...

    def positions_get(self, symbol: str) -> list[Mt5Position]: ...

    def order_send(self, request: dict) -> Mt5OrderSendResult: ...

    def order_check(self, request: dict) -> Mt5OrderCheckResult: ...

    def last_error(self) -> tuple[int, str]: ...
