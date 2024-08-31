import os

import pytest

skip_if_secret_not_set_bybit = pytest.mark.skipif(
    (os.environ.get("BYBIT_API_KEY") is None)
    or (os.environ.get("BYBIT_SECRET") is None),
    reason="bybit secret not set (maybe run in CI)",
)
