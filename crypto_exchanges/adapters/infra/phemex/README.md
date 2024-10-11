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
