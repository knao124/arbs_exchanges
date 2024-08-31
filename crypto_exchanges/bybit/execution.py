import pybotters


class BybitWsExecution:
    def __init__(self, store: pybotters.BybitUSDTDataStore):
        self._store = store

    def latest_executions(self) -> list:
        return self._store.execution._find_and_delete()
