from .i_balance_repository import IBalanceRepository
from .i_execution_repository import IExecutionRepository
from .i_fee_repository import IFeeRepository
from .i_order_book_repository import IOrderBookRepository
from .i_order_repository import IOrderRepository
from .i_position_repository import IPositionRepository


class IRestRepository(
    IOrderBookRepository,
    IExecutionRepository,
    IFeeRepository,
    IBalanceRepository,
    IPositionRepository,
):
    pass
