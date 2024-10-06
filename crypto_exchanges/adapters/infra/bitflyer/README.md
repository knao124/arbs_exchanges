## 実装メモ

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
