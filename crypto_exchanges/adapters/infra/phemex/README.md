## 実装メモ

### symbol

- ccxt 使う
- symbol は `BTC/USDT:USDT`

```python
import ccxt

bf = ccxt.phemex()
markets = bf.load_markets()
btc_markets = [m for m in markets if m.startswith("BTC")]
btc_markets
# ['BTC/USDT', 'BTC/TRY', 'BTC/USDC', 'BTC/BRZ', 'BTC/USD:BTC', 'BTC/USD:USD', 'BTC/USDT:USDT']
```

### fee

- 特殊な取り方をしないといけない

```python
res = ccxt_phemex.request(
    path="api-data/futures/fee-rate",
    api="private",
    method="GET",
    params={"settleCurrency": "USDT"},
)
for symbol_fee_rate in res["data"]["symbolFeeRates"]:
    if symbol_fee_rate["symbol"] == Symbol.PHEMEX_LINEAR_BTCUSDT.to_exchange_symbol():
        print(symbol_fee_rate)
```

### websocket

- テストネットは `wss://testnet-api.phemex.com/ws`
- 本番は `wss://ws.phemex.com`
- hedged の方
  - https://phemex-docs.github.io/#hedged-contract-websocket-api

orderbook

```python
async def main():
    async with pybotters.Client() as client:
        store = pybotters.PhemexDataStore()
        repo = PhemexWsRepository(store)

        await client.ws_connect(
            "wss://testnet-api.phemex.com/ws",
            send_json={
                "id": 1234,
                "method": "orderbook_p.subscribe",
                "params": ["BTCUSDT"],
            },
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.orderbook.sorted(limit=2)
            print(orderbook)

            await store.orderbook.wait()
            print(repo.fetch_order_book())


await main()
```

executions

```python
async def main():
    async with pybotters.Client() as client:
        store = pybotters.PhemexDataStore()
        repo = PhemexWsRepository(store)

        await client.ws_connect(
            "wss://testnet-api.phemex.com/ws",
            send_json={
                "id": 1234,
                "method": "trade_p.subscribe",
                "params": ["BTCUSDT"],
            },
            hdlr_json=store.onmessage,
        )

        while True:
            await store.trade.wait()
            executions = store.trade.find()
            print(executions)
```

position

```python
async def main():
    import os

    from crypto_exchanges.adapters.infra.phemex.phemex_order_repository import (
        PhemexOrderRepository,
    )
    from crypto_exchanges.adapters.resolvers.phemex import init_ccxt_phemex

    apis = {
        "phemex_testnet": [
            os.environ["PHEMEX_API_KEY_TESTNET"],
            os.environ["PHEMEX_SECRET_TESTNET"],
        ]
    }
    async with pybotters.Client(apis=apis) as client:
        store = pybotters.PhemexDataStore()
        repo = PhemexWsRepository(store)
        cc = init_ccxt_phemex(mode="testnet")
        orderer = PhemexOrderRepository(cc, Symbol.PHEMEX_LINEAR_BTCUSDT)

        await client.ws_connect(
            "wss://testnet-api.phemex.com/ws",
            send_json={
                "id": 1234,
                "method": "aop_p.subscribe",
                "params": [],
            },
            hdlr_json=store.onmessage,
        )

        orderer.create_market_order(Decimal("0.001"))
        while True:
            await store.positions.wait()
            positions = store.positions.find()
            print(positions)
            print(repo.fetch_positions())
```
