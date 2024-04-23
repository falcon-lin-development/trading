import json
from typing import List
from datetime import datetime
import pandas as pd

# custom
from settings import DATA_DIR, CONTANT_DIR
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

    @classmethod
    def from_dict(cls, dict_representation):
        return cls(**dict_representation)

    def to_series(self):
        # Convert coin's attributes to a Series
        data = {
            'dayNtlVlm': float(self.dayNtlVlm) if self.dayNtlVlm else None,
            'funding': float(self.funding) if self.funding else None,
            'impactPxs': self.impactPxs if self.impactPxs else None,
            'markPx': float(self.markPx) if self.markPx else None,
            'midPx': float(self.midPx) if self.midPx else None,
            'openInterest': float(self.openInterest) if self.openInterest else None,
            'oraclePx': float(self.oraclePx) if self.oraclePx else None,
            'premium': float(self.premium) if self.premium else None,
            'prevDayPx': float(self.prevDayPx) if self.prevDayPx else None,
            # Include other attributes as needed
        }
        return pd.Series(data)

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

    @classmethod
    def from_dict(cls, dict_representation):
        return cls(
            dict_representation["maxLeverage"],
            dict_representation["name"],
            dict_representation["onlyIsolated"],
            dict_representation["szDecimals"],
            MarketData.from_dict(dict_representation["marketData"]),
        )

    def to_series(self):
        # Convert coin's attributes to a Series
        data = {
            'maxLeverage': self.maxLeverage,
            'name': self.name,
            'onlyIsolated': self.onlyIsolated,
            'szDecimals': self.szDecimals,
            # Include other attributes as needed
        }
        data.update(self.marketData.to_series())
        return pd.Series(data)

class Market(PythonDictObject):
    """
        Keep track of a set of coins object
    """
    def __init__(self, coins: dict[str, Coin]):
        self.coins = coins

    ########## Methods ##########
    def export_coin_names(self):
        coins = list(self.coins.keys())
        file_path = CONTANT_DIR / "coin_names.py"
        with open(file_path, "w") as file:
            file.write(f"from enum import Enum\n\n")
            file.write(f"class CoinNames(Enum):\n")
            for coin in coins:
                file.write(f"    {coin} = '{coin}'\n")
        return f"Coin names exported to {file_path}"

    def get_coin(self, coin_name: str):
        return self.coins[coin_name].to_dict()

    def to_df(self):
        df = pd.DataFrame([coin.to_series() for coin in self.coins.values()])
        return df

    @classmethod
    def from_response(self, res):
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





    ########## storage ##########

    def to_json_file(self, file_path: str):
        ### Convert the Market object to a dictionary
        dict_representation = self.to_dict()

        ### Get the current date and time
        now = datetime.now()
        # Format the date and time as a string
        # dt = now.strftime("%Y-%m-%d-%H:%M:%S")
        dt = now.strftime("%Y-%m-%d")

        ### Write the dictionary to a JSON file
        # create directory if not exist
        if not (DATA_DIR / f"{dt}").exists():
            (DATA_DIR / f"{dt}").mkdir(parents=True, exist_ok=True)
        with open(DATA_DIR / f"{dt}" / file_path, "w") as file:
            json.dump(dict_representation, file, indent=4)

        with open(DATA_DIR / file_path, "w") as file:
            json.dump(dict_representation, file, indent=4)
        return f"Market object written to {file_path}"

    @classmethod
    def from_json_file(cls, file_path: str = "market.json"):
        # Read the dictionary from a JSON file
        with open(DATA_DIR / file_path, "r") as file:
            dict_representation = json.load(file)
        # Create a new Market object from the dictionary
        return cls.from_dict(dict_representation)

    @classmethod
    def from_dict(cls, dict_representation):
        coins = {}
        for coin_name, coin_dict in dict_representation["coins"].items():
            coins[coin_name] = Coin.from_dict(coin_dict)
        return cls(coins)