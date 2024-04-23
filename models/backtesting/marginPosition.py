from decimal import Decimal
from enum import Enum


class MarginPosition:
    slippage = Decimal("0.0001")  # 0.01% slippage
    transaction_cost = Decimal("0.00035")  # 0.035% transaction cost

    class Side(Enum):
        LONG = 1
        SHORT = 2

    def __init__(self, symbol, entry_price, equity, side, leverage=1.0):
        self.symbol = symbol
        self.entry_price = Decimal(entry_price)
        self.equity = Decimal(equity)
        self.side = side
        self.leverage = Decimal(leverage)
        self.size = (
            self.equity * self.leverage / self.entry_price
        )  # Number of units bought

    def pnl(self, current_price):
        current_price = Decimal(current_price)
        if self.side == self.Side.LONG:
            return (current_price - self.entry_price) * self.size
        else:  # SHORT position
            return (self.entry_price - current_price) * self.size

    def pnl_percentage(self, current_price):
        current_price = Decimal(current_price)
        return (self.pnl(current_price) / (self.equity)) * 100

    def liquidation_price(self):
        """
        https://leverage.trading/liquidation-price-calculator/
        """
        torlerance = self.entry_price * (1 / self.leverage)
        if self.side == self.Side.LONG:
            return self.entry_price - torlerance
        else:  # SHORT position
            return self.entry_price + torlerance

    def position_value(self, current_price):
        """
        Calculate the marketing value of the holding position.
        """
        current_price = Decimal(current_price)
        return self.size * current_price

    def position_evaluation(self, current_price):
        """
        Calculate the net amount received or paid when unwinding the position.
        """
        return self.equity + self.pnl(current_price)

    def __str__(self) -> str:
        return f"Symbol: {self.symbol}, Entry Price: {self.entry_price}, Equity: {self.equity}, Side: {self.side}, Leverage: {self.leverage}, Size: {self.size}"

    __repr__ = __str__


# Example usage:
# Initialize a position
if __name__ == "__main__":
    position = MarginPosition(
        symbol="BTC",
        entry_price=50000,
        equity=10000,
        side=MarginPosition.Side.SHORT,
        leverage=10,
    )
    current_price = 45000

    # Get position metrics
    print("Position Value:", position.position_value(current_price))
    print("P&L:", position.pnl(current_price))
    print("P&L Percentage:", position.pnl_percentage(current_price))
    # print("Current Margin:", position.current_margin(current_price))
    print("Liquidation Price:", position.liquidation_price())
    print("Amount Received on Unwind:", position.unwind_position(current_price))
