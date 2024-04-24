from decimal import Decimal
from enum import Enum


class MarginPosition:
    slippage = Decimal("0.0001")  # 0.01% slippage
    transaction_cost = Decimal("0.00035")  # 0.035% transaction cost

    class Side(Enum):
        LONG = 1
        SHORT = 2

    def __init__(
        self,
        symbol,
        entry_price,
        equity,
        side,
        leverage=1.0,
        stop_loss_percentage=0,
    ):
        self.symbol = symbol
        self.entry_price = Decimal(entry_price)
        self.equity = Decimal(equity)
        self.side = side
        self.leverage = Decimal(leverage)
        self.size = (
            self.equity * self.leverage / self.entry_price
        )  # Number of units bought
        self.stop_loss_percentage = Decimal(stop_loss_percentage)

    def pnl(self, current_price):
        current_price = Decimal(current_price)
        if self.side == self.Side.LONG:
            return (current_price - self.entry_price) * self.size
        else:  # SHORT position
            return (self.entry_price - current_price) * self.size

    # def pnl_percentage(self, current_price):
    #     current_price = Decimal(current_price)
    #     return (self.pnl(current_price) / (self.equity)) * 100

    # def liquidation_price(self):
    #     """
    #     https://leverage.trading/liquidation-price-calculator/
    #     """
    #     torlerance = self.entry_price * (1 / self.leverage)
    #     if self.side == self.Side.LONG:
    #         return self.entry_price - torlerance
    #     else:  # SHORT position
    #         return self.entry_price + torlerance

    # def position_value(self, current_price):
    #     """
    #     Calculate the marketing value of the holding position.
    #     """
    #     current_price = Decimal(current_price)
    #     return self.size * current_price

    def position_evaluation(self, current_price):
        """
        Calculate the net amount received or paid when unwinding the position.
        """
        return self.equity + self.pnl(current_price)

    def should_stop_loss(self, current_price):
        return (
            self.position_evaluation(current_price=current_price) / self.equity
            <= self.stop_loss_percentage
        )

    def __str__(self) -> str:
        return f"Symbol: {self.symbol}, Entry Price: {self.entry_price}, Equity: {self.equity}, Side: {self.side}, Leverage: {self.leverage}, Size: {self.size}"

    __repr__ = __str__


