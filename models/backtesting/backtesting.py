import pandas as pd

def validate_data(func):
    def wrapper(self, data, *args, **kwargs):
        if self.verbose:
            print("Validating data...")
        strategy = kwargs.get("strategy", None)
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"
        data_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "symbol",
            "datetime",
            "interval",
        ]
        assert set(data.columns).issuperset(
            set(data_cols)
        ), "data must have columns ['open', 'high', 'low', 'close', 'volume']"
        expected_dtypes = {
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "int64",
            "symbol": "object",  # object is typically used for strings
            "datetime": "datetime64[ns]",
            "interval": "object",
        }
        for col, expected_dtype in expected_dtypes.items():
            assert data[col].dtype == expected_dtype, f"Column '{col}' must be of type {expected_dtype}"
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
    def run_backtesting(self, data, strategy=None):
        if self.verbose:
            print("Start Running backtesting...")
            print(f"Data shape: {data.shape}")
            print(f"Strategy: {strategy}")

        self.strategy = strategy
        for i, row in data.iterrows():
            if self.verbose:
                print(f"Processing row {i}...")
            self.strategy(row, data.iloc[0:i, :])

        if self.verbose:
            print("Backtesting complete.")
