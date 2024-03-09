import json
from typing import List
from datetime import datetime
import pandas as pd


# custom
from settings import DATA_DIR, CONTANT_DIR
from models.base import PythonDictObject


class Candle(PythonDictObject):
    """
    {'T': 1705903199999,
    'c': '41124.0',
    'h': '41158.0',
    'i': '15m',
    'l': '41100.0',
    'n': 15,
    'o': '41158.0',
    's': 'BTC',
    't': 1705902300000,
    'v': '0.42952'},
    """

    def __init__(
        self,
        T: int,
        c: str,
        h: str,
        i: str,
        l: str,
        n: int,
        o: str,
        s: str,
        t: int,
        v: str,
    ):
        self.s = s  # symbol
        self.t = t  # tic
        self.T = T  # toc
        self.i = i  # interval
        self.n = n  # number of trades
        self.c = c  # close
        self.h = h  # high
        self.l = l  # low
        self.o = o  # open
        self.v = v  # volume
        self.end_time = datetime.utcfromtimestamp(self.T / 1000).strftime(
            "%Y-%m-%d-%H:%M:%S"
        )
        self.start_time = datetime.utcfromtimestamp(self.t / 1000).strftime(
            "%Y-%m-%d-%H:%M:%S"
        )

    @classmethod
    def from_dict(cls, dict_representation):
        return cls(**dict_representation)

    def to_series(self):
        return pd.Series(
            {
                "symbol": self.s,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "interval": self.i,
                "number_of_trades": self.n,
                "close": float(self.c),
                "high": float(self.h),
                "low": float(self.l),
                "open": float(self.o),
                "volume": float(self.v),
                "tic": self.t,
                "toc": self.T,
            }
        )


class CandleList(PythonDictObject):
    def __init__(self, candles: List[Candle]):
        if len(candles) == 0:
            raise ValueError("Candle list cannot be empty")
        self.candles = candles
        self.symbol = self.candles[0].s
        self.interval = self.candles[0].i  
        self.start_time = self.candles[0].start_time
        self.end_time = self.candles[-1].end_time
        self.number_of_candles = len(self.candles)

    ########## Methods ##########
    def to_df(self):
        # Convert coin's attributes to a Series
        data = [candle.to_series() for candle in self.candles]
        return pd.DataFrame(data)

    @classmethod
    def from_df(cls, df):
        candles = [Candle.from_dict(candle) for candle in df.to_dict(orient="records")]
        return cls(candles=candles)

    @classmethod
    def from_response(cls, res):
        return cls(candles=[Candle(**candle) for candle in res])

    ########## storage ##########
    def to_csv(self, file_name: str = None):
        if file_name is None:
            file_name = f"{self.symbol}.csv"

        df = self.to_df()
        file_path = DATA_DIR / file_name
        df.to_csv(file_path, index=False)

        ### Get the current date and time
        now = datetime.now()
        # Format the date and time as a string
        # dt = now.strftime("%Y-%m-%d-%H:%M:%S")
        # dt = now.strftime("%Y-%m-%d")
        data_range = f"{self.start_time}{self.end_time}"
        file_path_2 = DATA_DIR / data_range / file_name
        if not (DATA_DIR / f"{data_range}").exists():
            (DATA_DIR / f"{data_range}").mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path_2, index=False)

        return f"Candles exported to {file_path}"

    @classmethod
    def from_csv(cls, file_name: str = None, symbol: str = None):
        if file_name is None:
            file_name = f"{symbol}.csv"

        file_path = DATA_DIR / file_name
        df = pd.read_csv(file_path)
        return cls.from_df(df)
