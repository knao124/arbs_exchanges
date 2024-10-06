## 実装メモ

### symbol

- ccxt 使う
- symbol は `BTC/JPY:JPY`

```python
import ccxt
bf = ccxt.bitflyer()
markets = bf.load_markets()
btc_markets = [m for m in markets if m.startswith("BTC")]
btc_markets
# ['BTC/JPY', 'BTC/USD', 'BTC/EUR', 'BTC/JPY:JPY']
```

### balance

- 証拠金は collateral で取得できる. balance じゃない

### board の test

```python
async def main():
    async with pybotters.Client() as client:
        store = pybotters.bitFlyerDataStore()

        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_snapshot_FX_BTC_JPY"},
                    "id": 1,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_FX_BTC_JPY"},
                    "id": 2,
                },
            ],
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.board.sorted(limit=2)
            print(orderbook)

            await store.board.wait()
```

### executions の test

- https://bf-lightning-api.readme.io/docs/realtime-executions

```python

async def main():
    import os
    async with pybotters.Client() as client:
        store = pybotters.bitFlyerDataStore()

        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_executions_FX_BTC_JPY"},
                    "id": 1,
                },
            ],
            hdlr_json=store.onmessage,
        )

        while True:
            executions = store.executions.find()
            print(executions)
            await store.executions.wait()


await main()
```

### position の test

api keys の設定

- https://pybotters.readthedocs.io/ja/stable/user-guide.html#authentication

position のチャンネルはないが、position の REST API と child_order_events のチャンネルで自炊することができる

- https://pybotters.readthedocs.io/ja/stable/examples.html#trading-bot
- あとは bitFlyerDataStore の中身が詳しい

```python
async def main():
    import os

    apis = {
        "bitflyer": [
            os.environ["BITFLYER_API_KEY_TESTNET"],
            os.environ["BITFLYER_SECRET_TESTNET"],
        ],
    }

    cc = init_ccxt_bitflyer(mode="testnet")
    repo = BitflyerOrderRepository(cc, symbol=Symbol.BITFLYER_CFD_BTCJPY)
    rest_repo = BitflyerRestRepository(cc, 1.0)

    async with pybotters.Client(apis=apis) as client:
        store = pybotters.bitFlyerDataStore()

        print("initialize...")
        await store.initialize(
            client.get(
                "https://api.bitflyer.com/v1/me/getpositions",
                params={"product_code": "FX_BTC_JPY"},
            ),
            client.get(
                "https://api.bitflyer.com/v1/me/getchildorders",
                params={"product_code": "FX_BTC_JPY"},
            ),
        )

        print("initial positions")
        positions = store.positions.find()
        print("ws", positions)
        print("rest", rest_repo.fetch_positions(Symbol.BITFLYER_CFD_BTCJPY))

        print("connect ws...")
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "child_order_events"},
                    "id": 1,
                },
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_executions_FX_BTC_JPY"},
                    "id": 2,
                },
            ],
            hdlr_json=store.onmessage,
        )

        count = 0

        while True:
            print("wait positions...")
            positions = store.positions.find()
            print(positions)

            if count == 0:
                print("buy")
                repo.create_market_order(size_with_sign=0.01)
                count += 1
            elif count == 1:
                print("sell")
                pos = rest_repo.fetch_positions(Symbol.BITFLYER_CFD_BTCJPY)
                pos_all = sum(p.size_with_sign for p in pos)
                print(pos_all)
                repo.create_market_order(size_with_sign=-pos_all)
                count += 1

            print("wait executions...")
            await store.executions.wait()


await main()
```

```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

- このエラーがでてうまく行っていないな
- たまに rest で確認するコードにしておくと良さそう
