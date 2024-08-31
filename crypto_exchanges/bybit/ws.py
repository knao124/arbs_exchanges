import asyncio
import queue
from logging import getLogger
from typing import Tuple

import pybotters

logger = getLogger(__name__)


async def start_bybit_ws_inverse(api_key: str, secret: str, symbol: str, testnet: bool):
    client = pybotters.Client(
        apis={"bybit": [api_key, secret], "bybit_testnet": [api_key, secret]},
        base_url=_rest_endpoint(testnet),
    )
    store = pybotters.BybitInverseDataStore()

    channels = [
        f"trade.{symbol}",
        f"orderBookL2_25.{symbol}",
        "position",
    ]

    await client.ws_connect(
        url=_ws_endpoint_inverse(testnet),
        send_json={"op": "subscribe", "args": channels},
        hdlr_json=store.onmessage,
    )

    await asyncio.sleep(2)

    return client, store


# errorのmsgにアクセスできるように変更したpybotters.DataStore
class _BybitUSDTDataStore(pybotters.BybitUSDTDataStore):
    def __init__(self):
        super().__init__()
        self.errors = queue.Queue(maxsize=10)

    def _onmessage(self, msg, ws):
        if "error" in msg:
            self.errors.put(msg)
        return super()._onmessage(msg, ws)


async def start_bybit_ws_linear(
    api_key: str,
    secret: str,
    symbol: str,
    testnet: bool,
) -> Tuple[pybotters.Client, _BybitUSDTDataStore]:
    client = pybotters.Client(
        apis={"bybit": [api_key, secret], "bybit_testnet": [api_key, secret]},
        base_url=_rest_endpoint(testnet),
    )
    store = _BybitUSDTDataStore()
    await initialize_position(client, store, symbol)

    public_channels = [
        f"trade.{symbol}",
        f"orderBookL2_25.{symbol}",
    ]

    private_channels = [
        "position",
        "execution",
    ]

    logger.info(f"Start subscribe public channels: {public_channels}, {testnet=}")
    await client.ws_connect(
        url=_ws_endpoint_linear_public(testnet),
        send_json={"op": "subscribe", "args": public_channels},
        hdlr_json=store.onmessage,
    )

    logger.info(f"Start subscribe private channels: {private_channels}, {testnet=}")
    await client.ws_connect(
        url=_ws_endpoint_linear_private(testnet),
        send_json={"op": "subscribe", "args": private_channels},
        hdlr_json=store.onmessage,
    )

    while not all([len(w) for w in [store.orderbook]]):
        logger.debug("[WAITING SOCKET RESPONSE]")
        await store.wait()

        # 起動時にerrorが起きていた場合raiseする
        if not store.errors.empty():
            raise BaseException(f"Failed BybitDatastore init: {store.errors.get()}")

    return client, store


async def initialize_position(
    client: pybotters.Client,
    store: pybotters.BybitInverseDataStore or pybotters.BybitUSDTDataStore,
    symbol: str,
):
    if "USDT" in symbol:  # linear
        await store.initialize(
            client.get("/private/linear/position/list", params={"symbol": symbol}),
        )
    elif "USD" in symbol:  # inverse
        await store.initialize(
            client.get("/v2/private/position/list", params={"symbol": symbol}),
        )


def _rest_endpoint(testnet: bool):
    assert testnet in [True, False]

    if testnet:
        return "https://api-testnet.bybit.com"
    return "https://api.bybit.com"


def _ws_endpoint_inverse(testnet: bool):
    assert testnet in [True, False]

    if testnet:
        return "wss://stream-testnet.bybit.com/realtime"
    return "wss://stream.bybit.com/realtime"


def _ws_endpoint_linear_public(testnet: bool):
    assert testnet in [True, False]

    if testnet:
        return "wss://stream-testnet.bybit.com/realtime_public"
    return "wss://stream.bybit.com/realtime_public"


def _ws_endpoint_linear_private(testnet: bool):
    assert testnet in [True, False]

    if testnet:
        return "wss://stream-testnet.bybit.com/realtime_private"
    return "wss://stream.bybit.com/realtime_private"
