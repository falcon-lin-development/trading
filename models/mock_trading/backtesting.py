from .portfolio import Portfolio, Position, PositionType
from .strategy import LongTopShortLowStrategy


class BackTesting:
    """
    This class is for backtesting trading strategies
    """

    def __init__(
        self,
        initial_cash: float,
        data,
        testing=True,
        slippage_rate=0.0025,
        transaction_commission_rate=0.00025,
    ):
        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.slippage_rate = slippage_rate  # 0.3% slippage
        self.transaction_commission_rate = transaction_commission_rate  # 0.025%
        self.data = data
        self.testing = testing

    def run_strategy(self, trading_interval: int):
        """
        Run the strategy on the data
        """
        
        strategy = LongTopShortLowStrategy(
            portfolio=self.portfolio,
            testing_mode=self.testing,
            slippage_rate=self.slippage_rate,
            transaction_commission_rate=self.transaction_commission_rate,
        )
        strategy.set_data(self.data)

        for i, (index, data) in enumerate(self.future_data.groupby("start_time")):
            print(i)
            print(f"Running strategy on {index}")


            break
            strategy.run(
                data,
                self.portfolio,
                execute_mode=[]
            )
            # self.portfolio.print_portfolio()
            self.portfolio.print_cash()
            # break
