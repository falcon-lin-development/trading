from .portfolio import Portfolio, Position, PositionType
import pandas as pd
import numpy as np
from enum import Enum


def rank_column(df, column, ascending=False):
    _df = df.copy()
    col_name = f"rank_{column}"
    if col_name not in _df.columns:
        _df[col_name] = np.nan
    _df.loc[_df[col_name].isna(), col_name] = _df.groupby("start_time")[column].rank(
        ascending=ascending
    )
    return _df


class Strategy:
    def run(self, portfolio: Portfolio):
        """
        this strategy takes in the current portfolio and past data to execute trades
        """
        raise NotImplementedError("run() method must be implemented by the subclass.")


class ExecuteMode(Enum):
    """
    This class is for the different modes of executing a strategy
    """

    OPEN = "open"
    CLOSE = "close"
    HOLD = "hold"


class LongTopShortLowStrategy(Strategy):
    def __init__(
        self,
        portfolio: Portfolio,
        testing_mode=True,
        slippage_rate=0.003,
        transaction_commission_rate=0.00025,
    ):
        self.portfolio = portfolio
        self.data = None
        self.testing_mode = testing_mode
        self.slippage_rate = slippage_rate
        self.transaction_commission_rate = transaction_commission_rate

    def set_data(self, data):
        # if testing mode, then all data are put in the model at once
        self.data = self._prepare_data(data)

    def merge_data(self, new_raw_data: pd.DataFrame):
        """
        only use this method if you are not in testing mode
        """
        if self.testing_mode:
            raise ValueError("This method is only for non-testing mode")

        # Step 1: Append new raw data to the existing raw data set
        self.raw_data = pd.concat([self.raw_data, new_raw_data]).drop_duplicates(
            keep="last"
        )
        # Step 2: Determine the portion of the old data needed for context in rolling calculations
        # Here, 'window_size' should be defined as it is in your prepare_data method
        window_size = 7 * 24 * 4
        # Fetch the last 'window_size' records from the old data as context
        context_data = (
            self.raw_data.groupby(level=0)
            .apply(lambda df: df.iloc[-window_size:])
            .droplevel(0)
        )

        # Combine this context with the new raw data for processing
        combined_new_data = pd.concat([context_data, new_raw_data])

        # Step 3: Process the combined new data
        combined_new_data = pd.DataFrame(combined_new_data)
        processed_new_data = self.prepare_data(combined_new_data)

        # Step 4: Merge this processed new data with the existing processed data, avoiding reprocessing
        # Only keep entries from processed_new_data that are not already in self.data
        data = pd.concat([self.data, processed_new_data]).drop_duplicates(keep="last")

        return data.sort_index()

    def run(
        self,
        current_data: pd.DataFrame,
        portfolio: Portfolio,
        execute_modes: list[ExecuteMode],
    ):
        """
        This strategy buys the top 10% of coins and shorts the bottom 1% of coins
        """
        # calculate the rank done
        if not self.testing_mode:
            self.data = self.merge_data(current_data)

        current_time = current_data.index.get_level_values("start_time").min()
        relevent_data = self.data.loc[(slice(None), current_time), :]
        relevent_data = relevent_data.sort_values(by=["start_time", "rank"])
        print(current_time, relevent_data.shape)

        if ExecuteMode.OPEN in execute_modes:
            # open new positions at the beginning
            long_coins = relevent_data.groupby("start_time").head(10)
            # if (len(long_coins) > 6):
            #     print(long_coins.shape)
            #     print(long_coins)
                # raise ValueError("long_coins should not be more than 6")
            short_coins = relevent_data.groupby("start_time").tail(10)
            self.execute_open_position(portfolio, long_coins, short_coins)

        if ExecuteMode.CLOSE in execute_modes:
            # close all positions in the end
            self.execute_close_position(portfolio, current_data)

    def execute_open_position(self, portfolio: Portfolio, long_coins, short_coins):
        print(
            "long coins",
            long_coins.index.get_level_values(0).unique().tolist(),
            # long_coins.loc[:,"rank"].values,
            "short coins",
            short_coins.index.get_level_values(0).unique().tolist(),
            # short_coins.loc[:,"rank"].values,
        )
        print("long rank", long_coins.loc[:, "rank"].values, "short rank", short_coins.loc[:, "rank"].values)
        investment_per_coin = portfolio.cash / 20  # Divided among top 10 and bottom 10
        for indexs, row in short_coins.iterrows():
            symbol = indexs[0]
            if np.isnan(row["rank"]):
                continue
            portfolio.add_position(
                Position(
                    position_type=PositionType.SHORT,
                    symbol=symbol,
                    # quantity=1,
                    quantity=investment_per_coin
                    / (row["open"] * (1 + self.slippage_rate)),
                    price=row["open"] * (1 + self.slippage_rate),
                    time=row.name[0],
                ),
                transaction_commission_rate=self.transaction_commission_rate,
            )

        # Step 2: Buy the top 10% of coins (6 coins)
        for indexs, row in long_coins.iterrows():
            if np.isnan(row["rank"]):
                continue
            symbol = indexs[0]
            portfolio.add_position(
                Position(
                    position_type=PositionType.LONG,
                    symbol=symbol,
                    # quantity=1,
                    quantity=investment_per_coin
                    / (row["open"] * (1 + self.slippage_rate)),
                    price=row["open"] * (1 + self.slippage_rate),
                    time=row.name[0],
                ),
                transaction_commission_rate=self.transaction_commission_rate,
            )

    def execute_close_position(self, portfolio: Portfolio, current_data: pd.DataFrame):
        print("closing positions")
        for symbol, position in portfolio.positions.copy().items():
            if position.position_type == PositionType.LONG:
                portfolio.add_position(
                    Position(
                        position_type=PositionType.SHORT,
                        symbol=position.symbol,
                        quantity=position.quantity,
                        price=current_data.loc[(position.symbol,), "close"].iloc[0]
                        * (1 - self.slippage_rate),
                        time=current_data.index.get_level_values("start_time")[-1],
                    ),
                    transaction_commission_rate=0,
                )
            else:
                portfolio.add_position(
                    Position(
                        position_type=PositionType.LONG,
                        symbol=position.symbol,
                        quantity=position.quantity,
                        price=current_data.loc[(position.symbol,), "close"].iloc[0]
                        * (1 + self.slippage_rate),
                        time=current_data.index.get_level_values("start_time")[-1],
                    ),
                    transaction_commission_rate=0,
                )

    def _prepare_data(self, data: pd.DataFrame):
        """
        Prepare the data for the strategy
        """
        data = data.copy()
        window_size = 7 * 24 * 4  # Adjust this based on your exact data frequency
        prep_col = [
            "pct_change",
            "rolling_accumulated_pct_change",
            "rolling_variance_pct_change",
            "rank",
        ]
        for col in prep_col:
            if col not in data.columns:
                data[col] = np.nan
        ### pct chage
        data.loc[data["pct_change"].isna(), "pct_change"] = data.groupby(level=0)[
            "close"
        ].pct_change()
        ### rolling_acc_pct_change
        data.loc[
            data["rolling_accumulated_pct_change"].isna(),
            "rolling_accumulated_pct_change",
        ] = data.groupby(level=0)["pct_change"].transform(
            lambda x: (
                x.rolling(window=window_size, min_periods=1).apply(
                    lambda y: np.prod(1 + y / 100)
                )
                - 1
            )
            * 100
        )
        data.loc[
            data["rolling_variance_pct_change"].isna(), "rolling_variance_pct_change"
        ] = data.groupby(level=0)["pct_change"].transform(
            lambda x: x.rolling(window=window_size, min_periods=1).var()
        )
        data = rank_column(data, "rolling_accumulated_pct_change", ascending=False)
        data = rank_column(data, "rolling_variance_pct_change", ascending=True)
        data.loc[data["rank"].isna(), "rank"] = (
            data["rank_rolling_accumulated_pct_change"]
            + data["rank_rolling_variance_pct_change"]
        ) / 2
        return data
