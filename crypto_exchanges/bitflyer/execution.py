import pybotters


class BitflyerWsExecution:
    def __init__(self, store: pybotters.bitFlyerDataStore):
        self._store = store

    def latest_executions(self) -> list:
        return self._store.executions._find_and_delete()
