import asyncio
import datetime
import json
import queue
from decimal import Decimal
from logging import getLogger

import aiohttp
import pybotters

from arbs.logger import get_rotating_csv_logger

# ref: https://github.com/ko0hi/pybotters-magito-mm/blob/master/main.py
# ref: https://bf-lightning-api.readme.io/docs/realtime-executions


# 以下の変更を施したpybotters.DataStore
# - errorのmsgにアクセスできるように
# - 現物手数料を考慮に入れるように
class MyBitflyerDataStore(pybotters.bitFlyerDataStore):
    def __init__(self):
        super().__init__()
        self.errors = queue.Queue(maxsize=10)
        self._logger = get_rotating_csv_logger(
            filename="logs/ws_debug/bitflyer.log", max_bytes=10485760
        )

    def _onmessage(self, msg, ws):
        try:
            if "error" in msg:
                self._logger.error(msg)
                self.errors.put(msg)

            # monkeypatch: child_order_eventsの約定sizeから手数料で消えるsizeも差し引く
            if "params" in msg:
                channel: str = msg["params"]["channel"]
                message = msg["params"]["message"]
                if channel == "child_order_events":
                    for item in message:
                        if item["event_type"] == "EXECUTION":
                            side_int = 1 if item["side"] == "BUY" else -1
                            item["size"] = float(
                                Decimal(str(item["size"]))
                                - Decimal(str(item["commission"]))
                                * side_int  # BUYなら引く。SELLなら足す
                            )

                    # debug用にログ
                    msg["log_at"] = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                    self._logger.info(json.dumps(msg))

            self._onmessage_org(msg, ws)
        except BaseException as e:
            self._logger.error(
                f"BitflyerのWebsocketの処理中にエラーが発生しました. メッセージのログを記録しておきます. {e=}",
                exc_info=True,
            )
            self._logger.error(msg)

    # ポジションのズレの原因がpositions._onmessageを呼ぶ前にエラーがでているのでは？の仮説をつぶすため
    # いらない処理をコメントアウト
    # ref: https://github.com/knao124/arbs/issues/131#issuecomment-1304721925
    def _onmessage_org(self, msg, ws) -> None:
        # if "error" in msg:
        #     logger.warning(msg)
        if "params" in msg:
            channel: str = msg["params"]["channel"]
            message = msg["params"]["message"]
            if channel.startswith("lightning_board_"):
                if channel.startswith("lightning_board_snapshot_"):
                    asyncio.create_task(
                        ws.send_json(
                            {
                                "method": "unsubscribe",
                                "params": {"channel": channel},
                            }
                        )
                    )
                    product_code = channel.replace("lightning_board_snapshot_", "")
                    self.board._delete(self.board.find({"product_code": product_code}))
                    self._snapshots.add(product_code)
                else:
                    product_code = channel.replace("lightning_board_", "")
                if product_code in self._snapshots:
                    self.board._onmessage(product_code, message)
            elif channel.startswith("lightning_ticker_"):
                self.ticker._onmessage(message)
            elif channel.startswith("lightning_executions_"):
                product_code = channel.replace("lightning_executions_", "")
                self.executions._onmessage(product_code, message)
            elif channel == "child_order_events":
                # self.childorderevents._onmessage(message)
                # self.childorders._onmessage(message)
                self.positions._onmessage(message)
            # elif channel == "parent_order_events":
            #     self.parentorderevents._onmessage(message)
            #     self.parentorders._onmessage(message)


async def start_bitflyer_ws(
    api_key: str,
    secret: str,
    symbol: str,
    verify_ssl: bool = True,  # 基本Trueで良い. コメント参照
):

    _logger = getLogger(__name__)
    _logger.info("bitflyerのwebsocketの購読を開始します")

    client = pybotters.Client(
        apis={"bitflyer": [api_key, secret], "bitflyer_testnet": [api_key, secret]},
        base_url="https://api.bitflyer.com/v1/",
        # windows環境だとerrorが出るのでOFFできるようにした. 本当はよくない
        connector=aiohttp.TCPConnector(verify_ssl=verify_ssl),
    )

    store = MyBitflyerDataStore()
    await client.ws_connect(
        url="wss://ws.lightstream.bitflyer.com/json-rpc",
        send_json=[
            {
                "method": "subscribe",
                "params": {"channel": f"lightning_board_snapshot_{symbol}"},
                "id": 1,
            },
            {
                "method": "subscribe",
                "params": {"channel": f"lightning_board_{symbol}"},
                "id": 2,
            },
            {
                "method": "subscribe",
                "params": {"channel": "child_order_events"},
                "id": 3,
            },
            {
                "method": "subscribe",
                "params": {"channel": f"lightning_executions_{symbol}"},
                "id": 4,
            },
        ],
        hdlr_json=store.onmessage,
    )
    while not all([len(w) for w in [store.board, store.executions]]):
        _logger.debug("[WAITING SOCKET RESPONSE]")
        await store.wait()

        # 起動時にerrorが起きていた場合raiseする
        if not store.errors.empty():
            raise BaseException(f"Failed BitflyerDatastore init: {store.errors.get()}")

    _logger.debug("[SOCKET OPENED]")
    return client, store
