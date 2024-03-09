import json
from typing import List

# custom
from constant import DATA_DIR, CONTANT_DIR
from models.base import PythonDictObject


class MarketData(PythonDictObject):
    def __init__(
        self,
        dayNtlVlm: str,
        funding: str,
        impactPxs: List[str],
        markPx: str,
        midPx: str,
        openInterest: str,
        oraclePx: str,
        premium: str,
        prevDayPx: str,
    ):
        self.dayNtlVlm = dayNtlVlm
        self.funding = funding
        self.impactPxs = impactPxs
        self.markPx = markPx
        self.midPx = midPx
        self.openInterest = openInterest
        self.oraclePx = oraclePx
        self.premium = premium
        self.prevDayPx = prevDayPx


class Coin(PythonDictObject):
    def __init__(
        self,
        maxLeverage: int,
        name: str,
        onlyIsolated: bool,
        szDecimals: int,
        marketData: MarketData,
    ):
        self.maxLeverage = maxLeverage
        self.name = name
        self.onlyIsolated = onlyIsolated
        self.szDecimals = szDecimals
        self.marketData = marketData


class Market(PythonDictObject):
    def __init__(self, coins: dict[str, Coin]):
        self.coins = coins

    @classmethod
    def fromJson(self, res):
        coins = {}
        _universe: List = res[0]["universe"]
        _marketData: List = res[1]
        for u, m in zip(_universe, _marketData):
            coin = Coin(
                u["maxLeverage"],
                u["name"],
                u["onlyIsolated"],
                u["szDecimals"],
                MarketData(
                    m["dayNtlVlm"],
                    m["funding"],
                    m["impactPxs"],
                    m["markPx"],
                    m["midPx"],
                    m["openInterest"],
                    m["oraclePx"],
                    m["premium"],
                    m["prevDayPx"],
                ),
            )
            coins[coin.name] = coin
        return Market(coins)

    def from_dict(self, dict_representation):
        coins = {}
        for coin_name, coin_dict in dict_representation["coins"].items():
            coins[coin_name] = Coin.from_dict(coin_dict)
        return Market(coins)

    def export_coin_names(self):
        coins = list(self.coins.keys())
        file_path = CONTANT_DIR / "coin_names.py"
        with open(file_path, "w") as file:
            file.write(f"from enum import Enum\n\n")
            file.write(f"class CoinNames(Enum):\n")
            for coin in coins:
                file.write(f"    {coin} = '{coin}'\n")
        return f"Coin names exported to {file_path}"

    def to_json_file(self, file_path: str):
        # Convert the Market object to a dictionary
        dict_representation = self.to_dict()
        # Write the dictionary to a JSON file
        with open(DATA_DIR / file_path, "w") as file:
            json.dump(dict_representation, file, indent=4)
        return f"Market object written to {file_path}"

    def from_json_file(self, file_path: str):
        # Read the dictionary from a JSON file
        with open(DATA_DIR / file_path, "r") as file:
            dict_representation = json.load(file)
        # Create a new Market object from the dictionary
        return self.from_dict(dict_representation)
