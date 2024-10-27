from abc import ABC, abstractmethod
from logging import getLogger
from uuid import uuid4

from arbs_exchanges.core.use_cases import Ticker


class IOrderLinkIdGenerator(ABC):
    @abstractmethod
    def generate(self) -> str: ...


class BybitDefaultOrderLinkIdGenerator(IOrderLinkIdGenerator):
    def generate(self) -> str:
        return str(uuid4())


class BybitUSDJPYOrderLinkIdGenerator(IOrderLinkIdGenerator):
    def __init__(
        self,
        usdjpy_ticker: Ticker,
    ):
        self._usdjpy_ticker = usdjpy_ticker

        self._logger = getLogger(__class__.__name__)

    # 最新のUSDJPYのレート情報が入ったorder_link_idを生成する
    def generate(self) -> str:
        try:
            return self._generate_raw()
        except BaseException as e:
            self._logger.error(
                f"order_link_idのgeneratorでエラーが発生しました: {e}", exc_info=True
            )
        # エラーが起きたらuuid4を36文字で返す
        return self._generate_uuid4_str()[:36]

    def _generate_raw(self) -> str:
        # order_link_id: 最大36文字. 英数字と記号. 記号は - と _ がsupportされている
        price = self._usdjpy_ticker.last_price()
        uuid_str = self._generate_uuid4_str()

        # uuid4で - が入るので、priceとuuidの区切り文字には _ を使う
        original = f"{price:.3f}_{uuid_str}"

        # .は-にreplaceする
        replaced = original.replace(".", "-")

        # 最大36文字
        return replaced[:36]

    def _generate_uuid4_str(self) -> str:
        return str(uuid4())
