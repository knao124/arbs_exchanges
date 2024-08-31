import os

import pytest

skip_if_secret_not_set_bybit = pytest.mark.skipif(
    (os.environ.get("BYBIT_API_KEY") is None)
    or (os.environ.get("BYBIT_SECRET") is None),
    reason="bybit secret not set (maybe run in CI)",
)


def get_bybit_default_config() -> dict:
    return dict(
        bybit=dict(
            symbol="BTCUSDT",
            default_type="future",
            bybit_orderer=dict(
                settlement_symbol="USDT",
            ),
            make_position_chaser=dict(
                min_unit_size=0.001,
                target_size_short_only=True,
            ),
            effective_ticker=dict(amount=0.01),
        )
    )
