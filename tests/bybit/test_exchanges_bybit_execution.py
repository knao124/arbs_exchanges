import asyncio

import pytest

from crypto_exchanges import bybit

from .utils import get_bybit_default_config, skip_if_secret_not_set_bybit


@pytest.mark.asyncio
@skip_if_secret_not_set_bybit
async def test_bybit_execution(monkeypatch):
    config = get_bybit_default_config()
    client_set = await bybit.ws_client_set(config=config, testnet=True)

    # 注文して約定データを作る
    client_set.orderer.post_market_order(side_int=1, size=0.01)

    # 約定を監視する
    timeout = 5
    execs = []
    while len(execs) == 0:
        execs = client_set.execution.latest_executions()

        # timeoutの設定
        await asyncio.sleep(0.1)
        timeout -= 0.1
        if timeout < 0:
            raise BaseException("Something went wrong")

    assert len(execs) > 0
    # 二回目はなくなってる
    execs = client_set.execution.latest_executions()
    assert len(execs) == 0
    await client_set.pybotters_client.close()
