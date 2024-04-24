from .strategy import Strategy, Action
from .backtesting import TRADE_DATA_COLS
from .portfolio import Portfolio, Transaction
from .marginPosition import MarginPosition
from enum import Enum
import numpy as np
import pandas as pd


def calculate_bollinger_bands(data, window=20, k=2):
    """Calculate Bollinger Bands for the given data."""
    # Calculate the middle band, which is the moving average of the closing prices
    data = data.copy()
    data["Middle Band"] = data["close"].rolling(window=window).mean()

    # Calculate the rolling standard deviation
    rolling_std = data["close"].rolling(window=window).std()

    # Calculate upper and lower bands
    data["Upper Band"] = data["Middle Band"] + (rolling_std * k)
    data["Lower Band"] = data["Middle Band"] - (rolling_std * k)

    return data[["close", "Middle Band", "Upper Band", "Lower Band"]]


def update_bollinger_bands_efficiently(data, window=20, k=2):
    """Update Bollinger Bands only for new data, where they haven't been calculated."""
    # Create a mask for rows that need Bollinger Band calculations
    data = data.copy()
    prep_col = [
        "Middle Band",
    ]
    for col in prep_col:
        if col not in data.columns:
            data[col] = np.nan
    mask = data["Middle Band"].isna()

    # Calculate for missing entries only
    if mask.any():
        # Calculate the Middle Band using a rolling window
        data.loc[mask, "Middle Band"] = (
            data["close"].rolling(window=window).mean()[mask]
        )

        # Calculate rolling standard deviation on the fly for the rows that are masked
        data.loc[mask, "close_std"] = rolling_std = (
            data["close"].rolling(window=window).std()
        )

        # Update only where needed
        data.loc[mask, "Upper Band"] = (
            data.loc[mask, "Middle Band"] + (rolling_std * k)[mask]
        )
        data.loc[mask, "Lower Band"] = (
            data.loc[mask, "Middle Band"] - (rolling_std * k)[mask]
        )

    return data


class BollingerBandsState(Enum):
    """Enum for the state of the Bollinger Bands."""

    ABOVE_UPPER_BAND = 1
    BELOW_LOWER_BAND = 2
    WITHIN_BANDS = 3


class BollingerBandsReEntryStrategy(Strategy):
    # BUY_QUANTITY = 0.0001
    INITIAL_CAPITAL = 200
    BUY_EQUITY = 10
    LEVERAGE = 1
    VERBOSE = True
    K = 2
    STOP_LOSS_PERCENTAGE = 0.5

    @property
    def verbose(self):
        return self.VERBOSE

    @property
    def initial_capital(self):
        return self._initial_capital or self.INITIAL_CAPITAL

    @property
    def buy_equity(self):
        return self._buy_equity or self.BUY_EQUITY

    @property
    def leverage(self):
        return self._leverage or self.LEVERAGE

    @property
    def k(self):
        return self._k or self.K

    @property
    def stop_loss_percentage(self):
        return self._stop_loss_percentage or self.STOP_LOSS_PERCENTAGE

    def __init__(
        self,
        initial_capital=None,
        buy_equity=None,
        leverage=None,
        k=None,
        stop_loss_percentage=None,
    ):
        self._initial_capital = initial_capital
        self._buy_equity = buy_equity
        self._leverage = leverage
        self._k = k
        self._stop_loss_percentage = stop_loss_percentage

        self.data = pd.DataFrame(
            columns=[
                *TRADE_DATA_COLS,
                # "close",
                "Middle Band",
                "Upper Band",
                "Lower Band",
            ]
        )
        self.history = pd.DataFrame(
            columns=[
                "datetime",
                "symbol",
                "action",
                "price",
                "quantity",
            ]
        )
        self.portfolio = Portfolio(
            initial_capital=self.initial_capital,
        )

    counter = 0

    def run(self, current_data, historical_data):
        """Run the Bollinger Bands Re-Entry Strategy."""
        # handle the case where the current data is a series
        if isinstance(current_data, pd.Series):
            current_data = pd.DataFrame([current_data])
        for col in self.data.columns:
            if col not in current_data.columns:
                current_data[col] = np.nan
        current_data = current_data[self.data.columns]

        # Combine the current and historical data
        try:
            # print("-------- current data --------")
            # print(current_data, type(current_data))
            # print(self.data, type(self.data))
            self.data = pd.concat([self.data, current_data], axis=0, ignore_index=True)
            # print("-------- merged data --------")
            # print(self.data, type(self.data))

            # Update the Bollinger Bands
            self.data = update_bollinger_bands_efficiently(self.data, k=2)

            # Check the state of the Bollinger Bands
            self.data["state"] = self.data.apply(self.check_state, axis=1)

            # Execute trades based on the state
            self.execute_trades()
            history = self.portfolio.check_portfolio_state(current_data)
            if history is not None and history.shape[0] > 0:
                self.history = pd.concat([self.history, history], ignore_index=True)
            self.portfolio.evaluate_portfolio(current_data)
            if self.verbose:
                print(
                    "Portfolio Value: ",
                    self.portfolio.portfolio_history.shape,
                    ":",
                    self.portfolio.portfolio_history[-1:]["close"].values[0],
                )
        except Exception as e:
            print(e)
            print("Error in running the Bollinger Bands Re-Entry Strategy.")
            raise e

    def check_state(self, row):
        """Check the state of the Bollinger Bands."""
        if pd.isna(row["Middle Band"]):
            return np.nan

        if row["close"] > row["Upper Band"]:
            return BollingerBandsState.ABOVE_UPPER_BAND
        elif row["close"] < row["Lower Band"]:
            return BollingerBandsState.BELOW_LOWER_BAND
        else:
            return BollingerBandsState.WITHIN_BANDS

    def execute_trades(self):
        """Execute trades based on the transition of the Bollinger Bands state."""
        # Check if there's enough data to compare current and previous states

        if len(self.data) > 1:
            current_row = self.data.iloc[-1]
            previous_row = self.data.iloc[-2]

            if self.verbose:
                print(
                    "shape(self.data): ",
                    self.data.shape,
                    "states: ",
                    current_row["state"],
                    previous_row["state"],
                )

            # Check for state transition from OUTSIDE to WITHIN bands
            if (
                previous_row["state"] != BollingerBandsState.WITHIN_BANDS
                and current_row["state"] == BollingerBandsState.WITHIN_BANDS
            ):
                if previous_row["state"] == BollingerBandsState.ABOVE_UPPER_BAND:
                    self.short(current_row)
                    print("Sold at: ", current_row["close"])
                elif previous_row["state"] == BollingerBandsState.BELOW_LOWER_BAND:
                    self.long(current_row)
                    print("Bought at: ", current_row["close"])
            else:
                if self.verbose:
                    print("No valid trade condition met.")

    def long(self, row):
        """Buy shares of the stock."""
        action, position = self.portfolio.long(
            symbol=row["symbol"],
            equity=self.buy_equity,
            price=row["close"],
            date=row["datetime"],
            leverage=self.leverage,
            stop_loss_percentage=self.stop_loss_percentage,
        )

        history_action = None
        if action == Transaction.Side.OPEN_LONG:
            history_action = Action.LONG
        elif action == Transaction.Side.CLOSE_SHORT:
            history_action = Action.SHORT_UNWIND
        else:
            history_action = Action.MISSED_LONG

        self.history = pd.concat(
            [
                self.history,
                pd.DataFrame(
                    {
                        "datetime": row["datetime"],
                        "symbol": row["symbol"],
                        "action": history_action,
                        "price": row["close"],
                        "quantity": position.size,
                    },
                    index=[0],
                ),
            ],
            ignore_index=True,
        )

    def short(self, row):
        """Sell shares of the stock."""
        action, position = self.portfolio.short(
            row["symbol"],
            self.buy_equity,
            row["close"],
            row["datetime"],
            leverage=self.leverage,
            stop_loss_percentage=self.stop_loss_percentage,
        )

        history_action = None
        if action == Transaction.Side.OPEN_SHORT:
            history_action = Action.SHORT
        elif action == Transaction.Side.CLOSE_LONG:
            history_action = Action.LONG_UNWIND
        else:
            history_action = Action.MISSED_SHORT

        self.history = pd.concat(
            [
                self.history,
                pd.DataFrame(
                    {
                        "datetime": row["datetime"],
                        "symbol": row["symbol"],
                        "action": history_action,
                        "price": row["close"],
                        "quantity": position.size,
                    },
                    index=[0],
                ),
            ],
            ignore_index=True,
        )

    def end(self):
        """End the strategy."""
        self.portfolio.end()
        if self.verbose:
            print("End of the Bollinger Bands Re-Entry Strategy.")

    def plot_history(self, animate=False):
        """Plot the history of the strategy."""
        self.plotly_strategy(self.data, self.history, self.portfolio.portfolio_history)

    def plot_performance(self):
        """Plot the performance of the strategy."""
        self.plotly_portfolio(self.portfolio.portfolio_history)
