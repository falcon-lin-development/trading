from portfolio import Portfolio, Position, PositionType
import pandas as pd
import numpy as np


def rank_column(df, column, ascending=False):
    # Step 1: Set 'start_time' as part of the index if it's not already
    if (
        not isinstance(df.index, pd.MultiIndex)
        or "start_time" not in df.index.names
        or "coin" not in df.index.names
    ):
        # If 'coin' is not a column, create it from the index
        if "coin" not in df.columns:
            df["coin"] = df.index
        # Reset index if necessary and set 'start_time' and 'coin' as the index
        if "start_time" not in df.index.names:
            df = df.reset_index()
        df = df.set_index(["start_time", "coin"])

    # Step 2: Pivot the DataFrame
    # df_pivoted = df.pivot_table(values='rolling_accumulated_pct_change', index='start_time', columns='coin')
    df_pivoted = df.pivot_table(values=column, index="start_time", columns="coin")

    # Step 3: Rank the pivoted DataFrame
    df_ranked = df_pivoted.rank(axis=1, ascending=ascending)

    # Step 4: Melt the DataFrame back to long format
    df_ranked_melted = df_ranked.reset_index().melt(
        id_vars=["start_time"], var_name="coin", value_name=f"rank_{column}"
    )

    # Merge the rank back to the original DataFrame
    df_final = pd.merge(
        df.reset_index(),
        df_ranked_melted,
        left_on=["start_time", "symbol"],
        right_on=["start_time", "coin"],
        how="left",
    )
    df_final.drop(columns=["coin_x", "coin_y"], inplace=True)
    df_final.set_index(["symbol"], inplace=True)
    return df_final


class Strategy:
    def run(self, past_data: pd.DataFrame, portfolio: Portfolio):
        """
        this strategy takes in the current portfolio and past data to execute trades
        """
        raise NotImplementedError("run() method must be implemented by the subclass.")


class LongTopShortLowStrategy(Strategy):
    HOLDING_PERIOD = 1
    def __init__(self, data: pd.DataFrame):
        self.raw_data = data.copy()
        self.data = self.prepare_data(data)
        self.holding_period = None

    def prepare_data(self, data: pd.DataFrame):
        """
        Prepare the data for the strategy
        """
        ### pct chage
        data["pct_change"] = data.groupby(level=0)["close"].pct_change()
        ### rolling_acc_pct_change
        window_size = 7 * 24 * 4  # Adjust this based on your exact data frequency
        data["rolling_accumulated_pct_change"] = data.groupby(level=0)[
            "pct_change"
        ].transform(
            lambda x: (
                x.rolling(window=window_size, min_periods=1).apply(
                    lambda y: np.prod(1 + y / 100)
                )
                - 1
            )
            * 100
        )
        data["rolling_variance_pct_change"] = data.groupby(level=0)[
            "pct_change"
        ].transform(lambda x: x.rolling(window=window_size, min_periods=1).var())
        data = rank_column(data, "rolling_accumulated_pct_change", ascending=False)
        data = rank_column(data, "rolling_variance_pct_change", ascending=True)
        data["rank"] = (
            data["rank_rolling_accumulated_pct_change"]
            + data["rank_rolling_variance_pct_change"]
        ) / 2
        return data

    def merge_data(self, new_raw_data: pd.DataFrame):
        # Step 1: Append new raw data to the existing raw data set
        new_raw_data.set_index(["symbol", "start_time"], inplace=True)
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
        processed_new_data = self.prepare_data(combined_new_data)

        # Step 4: Merge this processed new data with the existing processed data, avoiding reprocessing
        # Only keep entries from processed_new_data that are not already in self.data
        self.data = pd.concat([self.data, processed_new_data]).drop_duplicates(
            keep="last"
        )

    def run(
        self,
        current_data: pd.DataFrame,
        portfolio: Portfolio,
        slippage_rate: float = 0.003,
        transaction_commission_rate: float = 0.00025,
    ):
        """
        This strategy buys the top 10% of coins and shorts the bottom 1% of coins
        """
        # calculate the rank done
        self.merge_data(current_data)
        relevent_window = 1
        relevent_data = (
            self.data.groupby(level=0)
            .apply(lambda df: df.iloc[-relevent_window:])
            .droplevel(0)
        )
        relevent_data.sort_values(by=["start_time", "rank"], inplace=True)

        if self.holding_period is None:
            self.holding_period = self.HOLDING_PERIOD
            # Step 1: Sell the bottom 10% of coins (6 coins)
            short_coins = relevent_data.head(6)
            long_coins = relevent_data.tail(6)
            for symbol, row in short_coins.iterrows():
                portfolio.add_position(
                    Position(
                        position_type=PositionType.SHORT,
                        symbol=symbol,
                        quantity=1,
                        price=row["open"] * (1 + slippage_rate),
                        time=row["start_time"],
                    ),
                    transaction_commission_rate=transaction_commission_rate,
                )

            # Step 2: Buy the top 10% of coins (6 coins)
            for symbol, row in long_coins.iterrows():
                portfolio.add_position(
                    Position(
                        position_type=PositionType.LONG,
                        symbol=symbol,
                        quantity=1,
                        price=row["open"] * (1 + slippage_rate),
                        time=row["start_time"],
                    ),
                    transaction_commission_rate=transaction_commission_rate,
                )
        
        if self.holding_period > 0:
            self.holding_period -= 1

        if self.holding_period == 0:
            self.holding_period = None
            for symbol, position in portfolio.positions.items():
                if position.position_type == PositionType.LONG:
                    portfolio.add_position(
                        Position(
                            position_type=PositionType.SHORT,
                            symbol=position.symbol,
                            quantity=position.quantity,
                            price=relevent_data.loc[position.symbol, "close"] * (1 - slippage_rate),
                            time=current_data.index[-1],
                        ),
                        transaction_commission_rate=0,
                    )
                else:
                    portfolio.add_position(
                        Position(
                            position_type=PositionType.LONG,
                            symbol=position.symbol,
                            quantity=position.quantity,
                            price=relevent_data.loc[position.symbol, "close"] * (1 + slippage_rate),
                            time=current_data.index[-1],
                        ),
                        transaction_commission_rate=0,
                    )

class BackTesting:
    """
    This class is for backtesting trading strategies
    """

    def __init__(self, initial_cash: float, data):
        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.slippage_rate = 0.003  # 0.3% slippage
        self.transaction_commission_rate = 0.00025  # 0.025%
        self.data = data

    def run_strategy(self, trading_interval: int):
        """
        Run the strategy on the data
        """
        strategy = LongTopShortLowStrategy(self.data)
        for i in range(0, len(self.data), trading_interval):
            current_data = self.data.iloc[i : i + trading_interval]
            strategy.run(
                current_data,
                self.portfolio,
                slippage_rate=self.slippage_rate,
                transaction_commission_rate=self.transaction_commission_rate,
            )
