from typing import Optional


class DummyTrade:
    def __init__(self, data: Optional[list[dict]] = None):
        self.data = data

    def find(self) -> list[dict]:
        if self.data is not None:
            assert isinstance(self.data, list)
            if len(self.data) > 0:
                assert isinstance(self.data[0], dict)
                assert "T" in self.data[0]
                assert "s" in self.data[0]
                assert "S" in self.data[0]
                assert "v" in self.data[0]
                assert "p" in self.data[0]
                assert "L" in self.data[0]
                assert "i" in self.data[0]
            return self.data
        return [
            {
                "T": 1725093054120,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.001",
                "p": "59065.80",
                "L": "PlusTick",
                "i": "5ed00281-0d1a-54f4-85be-809e932d04b5",
                "BT": False,
            },
            {
                "T": 1725093055313,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.003",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "4d16da22-40b7-578b-ae17-0cabe1170391",
                "BT": False,
            },
            {
                "T": 1725093055486,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.038",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "4db0c5a3-a622-5384-af14-46c2494a4905",
                "BT": False,
            },
            {
                "T": 1725093055566,
                "s": "BTCUSDT",
                "S": "Sell",
                "v": "0.002",
                "p": "59065.70",
                "L": "MinusTick",
                "i": "4a5a811f-50f5-585c-8ca0-593885af062e",
                "BT": False,
            },
            {
                "T": 1725093055900,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.042",
                "p": "59065.80",
                "L": "PlusTick",
                "i": "26bdf055-0b50-5ccb-91f2-8ae1e2694521",
                "BT": False,
            },
            {
                "T": 1725093056159,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.042",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "83c1fe1a-bd5c-5118-bd71-4f0a7de45a58",
                "BT": False,
            },
            {
                "T": 1725093058482,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.004",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "9da24438-c94c-5013-a520-afccc0ae74a5",
                "BT": False,
            },
            {
                "T": 1725093059305,
                "s": "BTCUSDT",
                "S": "Sell",
                "v": "0.011",
                "p": "59065.70",
                "L": "MinusTick",
                "i": "60748655-86d4-5f09-8daa-ff6ef96d54c3",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.182",
                "p": "59065.80",
                "L": "PlusTick",
                "i": "25130e0a-dffe-5db5-891f-233eb158ec0e",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.002",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "4e1386a0-721f-55e7-a40b-851c4a64d0b2",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.002",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "ed6aab56-02d1-5baf-8736-b3d0cc39e07b",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.002",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "ae854afd-ab0e-5833-ab11-b94645a84ec5",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.161",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "db5bc4e3-efdf-51b1-8386-16a8a56525d7",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.005",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "0a94b304-82fa-5f9f-9dc4-5a3d21999f39",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.010",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "fb54c3f8-e512-5bdd-85dd-6e49101d3a60",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.006",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "847ac38f-2d4a-5a1e-9e9e-c98ddd6083ca",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.002",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "eef1601c-adc4-5271-93eb-e14ea3fd3e3d",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.034",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "b9fc0316-1628-57fb-a1a4-e47e84f65f9a",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.003",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "be7e9e6f-3c59-501c-bf1e-2f2c1377c9f5",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.100",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "2a86def4-9bb0-5c55-bfec-859734aade78",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.003",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "0d110060-2d8f-5e32-9ba7-68758f099a45",
                "BT": False,
            },
            {
                "T": 1725093061083,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.054",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "ee61ce92-a89a-571e-8446-0c721c62b3ff",
                "BT": False,
            },
            {
                "T": 1725093061786,
                "s": "BTCUSDT",
                "S": "Sell",
                "v": "0.004",
                "p": "59065.70",
                "L": "MinusTick",
                "i": "fc06a50b-70e7-556f-a3d9-1c110228d68b",
                "BT": False,
            },
            {
                "T": 1725093061919,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.079",
                "p": "59065.80",
                "L": "PlusTick",
                "i": "afbeaa93-612d-5f8a-94de-d40c474f8ba4",
                "BT": False,
            },
            {
                "T": 1725093062010,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.143",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "aa00b5de-2409-56b0-a62b-02aec0ff37f9",
                "BT": False,
            },
            {
                "T": 1725093062010,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.065",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "fb32070e-7da4-5212-b714-8d2e6e25ac29",
                "BT": False,
            },
            {
                "T": 1725093062289,
                "s": "BTCUSDT",
                "S": "Buy",
                "v": "0.001",
                "p": "59065.80",
                "L": "ZeroPlusTick",
                "i": "839597f6-a5ef-5e55-8b53-858f784e0e4c",
                "BT": False,
            },
            {
                "T": 1725093062850,
                "s": "BTCUSDT",
                "S": "Sell",
                "v": "0.699",
                "p": "59065.70",
                "L": "MinusTick",
                "i": "4666cf86-4fef-5850-9b14-c5a30ba00f83",
                "BT": False,
            },
            {
                "T": 1725093062850,
                "s": "BTCUSDT",
                "S": "Sell",
                "v": "0.301",
                "p": "59065.70",
                "L": "ZeroMinusTick",
                "i": "2873b014-4cf4-5fe6-8613-dd3782f6abcc",
                "BT": False,
            },
            {
                "T": 1725093062944,
                "s": "BTCUSDT",
                "S": "Sell",
                "v": "0.005",
                "p": "59065.70",
                "L": "ZeroMinusTick",
                "i": "23c50297-9749-5e4a-ac33-09f24f043d39",
                "BT": False,
            },
        ]


class DummyOrderbook:
    def __init__(self, data: Optional[dict] = None):
        self.data = data

    def sorted(self) -> dict:
        if self.data is not None:
            assert isinstance(self.data, dict)
            assert "a" in self.data
            assert "b" in self.data
            for side in ["a", "b"]:
                if len(self.data[side]) > 0:
                    item = self.data[side][0]
                    assert isinstance(item, dict)
                    assert "s" in item
                    assert "S" in item
                    assert "p" in item
                    assert "v" in item
            return self.data
        return {
            "a": [
                {"s": "BTCUSDT", "S": "a", "p": "59072.10", "v": "11.481"},
                {"s": "BTCUSDT", "S": "a", "p": "59072.20", "v": "0.001"},
                {"s": "BTCUSDT", "S": "a", "p": "59072.50", "v": "1.254"},
                {"s": "BTCUSDT", "S": "a", "p": "59073.00", "v": "0.214"},
                {"s": "BTCUSDT", "S": "a", "p": "59073.20", "v": "0.263"},
                {"s": "BTCUSDT", "S": "a", "p": "59073.80", "v": "0.006"},
                {"s": "BTCUSDT", "S": "a", "p": "59074.00", "v": "0.165"},
                {"s": "BTCUSDT", "S": "a", "p": "59074.10", "v": "0.055"},
                {"s": "BTCUSDT", "S": "a", "p": "59075.20", "v": "0.002"},
                {"s": "BTCUSDT", "S": "a", "p": "59075.30", "v": "1.216"},
                {"s": "BTCUSDT", "S": "a", "p": "59075.60", "v": "0.006"},
                {"s": "BTCUSDT", "S": "a", "p": "59075.70", "v": "1.554"},
                {"s": "BTCUSDT", "S": "a", "p": "59075.90", "v": "0.011"},
                {"s": "BTCUSDT", "S": "a", "p": "59076.00", "v": "3.213"},
                {"s": "BTCUSDT", "S": "a", "p": "59076.10", "v": "0.004"},
                {"s": "BTCUSDT", "S": "a", "p": "59076.50", "v": "0.204"},
                {"s": "BTCUSDT", "S": "a", "p": "59076.70", "v": "1.554"},
                {"s": "BTCUSDT", "S": "a", "p": "59076.80", "v": "2.358"},
                {"s": "BTCUSDT", "S": "a", "p": "59076.90", "v": "0.014"},
                {"s": "BTCUSDT", "S": "a", "p": "59077.10", "v": "0.017"},
                {"s": "BTCUSDT", "S": "a", "p": "59077.60", "v": "0.006"},
                {"s": "BTCUSDT", "S": "a", "p": "59077.90", "v": "0.321"},
                {"s": "BTCUSDT", "S": "a", "p": "59078.00", "v": "0.164"},
                {"s": "BTCUSDT", "S": "a", "p": "59078.10", "v": "0.001"},
                {"s": "BTCUSDT", "S": "a", "p": "59078.20", "v": "0.002"},
                {"s": "BTCUSDT", "S": "a", "p": "59078.40", "v": "0.006"},
                {"s": "BTCUSDT", "S": "a", "p": "59078.70", "v": "0.508"},
                {"s": "BTCUSDT", "S": "a", "p": "59078.90", "v": "0.005"},
                {"s": "BTCUSDT", "S": "a", "p": "59079.00", "v": "0.006"},
                {"s": "BTCUSDT", "S": "a", "p": "59079.10", "v": "0.556"},
                {"s": "BTCUSDT", "S": "a", "p": "59079.40", "v": "2.129"},
                {"s": "BTCUSDT", "S": "a", "p": "59079.50", "v": "0.025"},
                {"s": "BTCUSDT", "S": "a", "p": "59079.60", "v": "2.592"},
                {"s": "BTCUSDT", "S": "a", "p": "59079.70", "v": "0.072"},
                {"s": "BTCUSDT", "S": "a", "p": "59079.90", "v": "0.034"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.00", "v": "0.204"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.10", "v": "1.719"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.20", "v": "0.259"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.30", "v": "0.145"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.40", "v": "0.007"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.50", "v": "3.554"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.70", "v": "0.034"},
                {"s": "BTCUSDT", "S": "a", "p": "59080.80", "v": "0.041"},
                {"s": "BTCUSDT", "S": "a", "p": "59081.00", "v": "0.058"},
                {"s": "BTCUSDT", "S": "a", "p": "59081.10", "v": "0.017"},
                {"s": "BTCUSDT", "S": "a", "p": "59081.20", "v": "0.007"},
                {"s": "BTCUSDT", "S": "a", "p": "59081.30", "v": "0.418"},
                {"s": "BTCUSDT", "S": "a", "p": "59081.40", "v": "0.115"},
                {"s": "BTCUSDT", "S": "a", "p": "59081.50", "v": "0.042"},
                {"s": "BTCUSDT", "S": "a", "p": "59081.70", "v": "0.021"},
            ],
            "b": [
                {"s": "BTCUSDT", "S": "b", "p": "59072.00", "v": "5.795"},
                {"s": "BTCUSDT", "S": "b", "p": "59071.00", "v": "0.118"},
                {"s": "BTCUSDT", "S": "b", "p": "59070.20", "v": "0.017"},
                {"s": "BTCUSDT", "S": "b", "p": "59070.10", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59070.00", "v": "0.157"},
                {"s": "BTCUSDT", "S": "b", "p": "59069.80", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59069.70", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59069.00", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59068.70", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59068.30", "v": "0.115"},
                {"s": "BTCUSDT", "S": "b", "p": "59068.10", "v": "0.008"},
                {"s": "BTCUSDT", "S": "b", "p": "59068.00", "v": "0.188"},
                {"s": "BTCUSDT", "S": "b", "p": "59067.80", "v": "0.021"},
                {"s": "BTCUSDT", "S": "b", "p": "59067.70", "v": "0.020"},
                {"s": "BTCUSDT", "S": "b", "p": "59067.60", "v": "0.004"},
                {"s": "BTCUSDT", "S": "b", "p": "59067.30", "v": "0.002"},
                {"s": "BTCUSDT", "S": "b", "p": "59066.90", "v": "0.512"},
                {"s": "BTCUSDT", "S": "b", "p": "59066.70", "v": "0.012"},
                {"s": "BTCUSDT", "S": "b", "p": "59066.60", "v": "0.847"},
                {"s": "BTCUSDT", "S": "b", "p": "59066.50", "v": "0.002"},
                {"s": "BTCUSDT", "S": "b", "p": "59066.20", "v": "0.457"},
                {"s": "BTCUSDT", "S": "b", "p": "59066.00", "v": "0.468"},
                {"s": "BTCUSDT", "S": "b", "p": "59065.70", "v": "0.846"},
                {"s": "BTCUSDT", "S": "b", "p": "59065.60", "v": "0.055"},
                {"s": "BTCUSDT", "S": "b", "p": "59065.50", "v": "0.089"},
                {"s": "BTCUSDT", "S": "b", "p": "59065.00", "v": "0.014"},
                {"s": "BTCUSDT", "S": "b", "p": "59064.50", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59064.40", "v": "0.010"},
                {"s": "BTCUSDT", "S": "b", "p": "59064.00", "v": "1.238"},
                {"s": "BTCUSDT", "S": "b", "p": "59063.90", "v": "2.069"},
                {"s": "BTCUSDT", "S": "b", "p": "59063.70", "v": "0.057"},
                {"s": "BTCUSDT", "S": "b", "p": "59063.50", "v": "0.126"},
                {"s": "BTCUSDT", "S": "b", "p": "59063.20", "v": "0.865"},
                {"s": "BTCUSDT", "S": "b", "p": "59063.10", "v": "0.263"},
                {"s": "BTCUSDT", "S": "b", "p": "59063.00", "v": "0.030"},
                {"s": "BTCUSDT", "S": "b", "p": "59062.50", "v": "0.204"},
                {"s": "BTCUSDT", "S": "b", "p": "59062.20", "v": "0.011"},
                {"s": "BTCUSDT", "S": "b", "p": "59062.10", "v": "0.034"},
                {"s": "BTCUSDT", "S": "b", "p": "59061.90", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59061.80", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59061.70", "v": "0.004"},
                {"s": "BTCUSDT", "S": "b", "p": "59061.50", "v": "0.040"},
                {"s": "BTCUSDT", "S": "b", "p": "59061.10", "v": "0.051"},
                {"s": "BTCUSDT", "S": "b", "p": "59060.60", "v": "0.002"},
                {"s": "BTCUSDT", "S": "b", "p": "59060.50", "v": "0.034"},
                {"s": "BTCUSDT", "S": "b", "p": "59060.40", "v": "0.778"},
                {"s": "BTCUSDT", "S": "b", "p": "59060.30", "v": "1.182"},
                {"s": "BTCUSDT", "S": "b", "p": "59060.10", "v": "0.001"},
                {"s": "BTCUSDT", "S": "b", "p": "59060.00", "v": "0.241"},
                {"s": "BTCUSDT", "S": "b", "p": "59059.90", "v": "0.949"},
            ],
        }


class BybitMockDataStore:
    def __init__(
        self, orderbook: Optional[dict] = None, trade: Optional[list[dict]] = None
    ):
        self.orderbook = DummyOrderbook(data=orderbook)
        self.trade = DummyTrade(data=trade)