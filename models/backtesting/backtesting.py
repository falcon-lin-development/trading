import pandas as pd
import pprint 

TRADE_DATA_COLS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
    "datetime",
    "interval",
]

EXPECTED_DTYPES = expected_dtypes = {
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "float64",
    "symbol": "object",  # object is typically used for strings
    "datetime": "datetime64[ns]",
    "interval": "object",
}

def validate_data(func):
    def wrapper(self, data, *args, **kwargs):
        if self.verbose:
            print("Validating data...")
        strategy = kwargs.get("strategy", None)
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"

        assert set(data.columns).issuperset(
            set(TRADE_DATA_COLS)
        ), f"data must have columns {TRADE_DATA_COLS}"
        for col, EXPECTED_DTYPE in EXPECTED_DTYPES.items():
            assert data[col].dtype == EXPECTED_DTYPE, f"Column '{col}' must be of type {EXPECTED_DTYPES[col]}"
        assert strategy is not None, "strategy must be provided"
        if self.verbose:
            print("Data validated successfully.")
        return func(self, data, *args, **kwargs)
    return wrapper

class BackTesting:
    """
    This class is for backtesting trading strategies
    """

    def __init__(
        self,
        verbose=True,
    ):
        self.verbose = verbose
        self.strategy = None

    @validate_data
    def run_backtesting(self, data, strategy=None, play_mode=False):
        if self.verbose:
            print("Start Running backtesting...")
            print(f"Data shape: {data.shape}")
            print(f"Strategy: {strategy}")

        self.strategy = strategy
        for i, row in data.iterrows():
            if self.verbose:
                print(f"Processing row {i}...")
            self.strategy.run(row, data.iloc[0:i, :])

            if play_mode:
                print(row["close"])
                print(self.strategy.portfolio.cash)
                pprint.pprint(self.strategy.portfolio.holdings)

                input("Press Enter to continue to the next step...")  # Pause execution
        else:
            self.strategy.end()


        if self.verbose:
            print("Backtesting complete.")

