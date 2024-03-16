import pandas as pd
from .portfolio import Portfolio, Position, PositionType
from .strategy import ExecuteMode, LongTopShortLowStrategy


class BackTesting:
    """
    This class is for backtesting trading strategies
    """

    def __init__(
        self,
        initial_cash: float,
        data,
        testing=True,
        slippage_rate=0.003,
        transaction_commission_rate=0.00025,
        verbose=False,
    ):
        self.portfolio = Portfolio(initial_cash=initial_cash, verbose=verbose)
        self.slippage_rate = slippage_rate  # 0.3% slippage
        self.transaction_commission_rate = transaction_commission_rate  # 0.025%
        self.data = data
        self.testing = testing

    def run_strategy(self, trading_interval: int, loop=None):
        """
        Run the strategy on the data
        """

        strategy = LongTopShortLowStrategy(
            portfolio=self.portfolio,
            testing_mode=self.testing,
            slippage_rate=self.slippage_rate,
            transaction_commission_rate=self.transaction_commission_rate,
        )
        # strategy.set_data(self.data)
        strategy.data = pd.read_csv("data.csv", parse_dates=[1, 2])
        strategy.data.set_index(["symbol", "start_time"], inplace=True)

        current = -1
        results = []
        for i, (index, data) in enumerate(self.data.groupby("start_time")):
            current += 1
            if loop is not None and current == loop:
                break
            print(
                "-------",
                "loop: ",
                i,
                "i % interval: ",
                i % trading_interval,
                "data shape",
                data.shape,
                "-------",
            )
            print(f"Running strategy on {index}")

            before_balance = self.portfolio.total_balance(current_data=data)
            actions = []
            if i % trading_interval == 0:
                actions.append(ExecuteMode.OPEN)
            if i % trading_interval == trading_interval - 1:
                actions.append(ExecuteMode.CLOSE)

            strategy.run(data, self.portfolio, execute_modes=actions)

            results.append(
                {
                    "timestamp": index,
                    "return": self.portfolio.total_balance(current_data=data) - before_balance,
                    "principal": self.portfolio.total_balance(current_data=data),
                }
            )
            # self.portfolio.print_portfolio()
            # self.portfolio.print_cash()
            self.portfolio.print_total_balance(current_data=data)

        return pd.DataFrame(results)
            # break
