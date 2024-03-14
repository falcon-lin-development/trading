from enum import Enum

import pandas as pd


class PositionType(Enum):
    LONG = "long"
    SHORT = "short"


class Position:
    def __init__(self, position_type, symbol, quantity, price, time):
        self.position_type: PositionType = position_type
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.time = time

    def __repr__(self):
        return f"{self.time}: {self.position_type} {self.quantity} {self.symbol} @ {self.price}"


class Portfolio:
    def __init__(self, initial_cash, verbose=False):
        self.cash = initial_cash
        self.positions = {}
        self.verbose = verbose

    def add_cash(self, amount):
        self.cash += amount

    def remove_cash(self, amount):
        if amount > self.cash:
            print("Insufficient funds.")
            raise ValueError("Insufficient funds.")
            # return False
        self.cash -= amount

    def add_position(self, position, transaction_commission_rate):
        """
        Add a new position to the portfolio
        1) if position already exists, combine the positions
            -> if position is the same type, add the quantities, weighted average the price
            -> if position is the opposite type, subtract the quantities, use the price of the larger position

        2) if position does not exist, add the position to the portfolio

        3) if the cost of the position is greater than the cash, do not add the position
        """
        if self.verbose:
            print(
                f"{position.position_type} {position.symbol}  {position.quantity} @ {position.price} "
            )
            old_cash = self.cash
            print(f"Current cash: {self.cash}", end=" ")
        ######## add/remove cash ########
        if position.position_type == PositionType.LONG:
            cost = position.quantity * position.price
            transaction_commission = cost * transaction_commission_rate
            self.remove_cash(cost)
            self.remove_cash(transaction_commission)

        else:
            cost = position.quantity * position.price
            transaction_commission = cost * transaction_commission_rate
            self.add_cash(cost)
            self.remove_cash(transaction_commission)

        if self.verbose:
            print(
                f"New cash: {self.cash}: +- {cost} - {transaction_commission} : total {self.cash-old_cash}"
            )

        ######## add the position to the portfolio ########
        if position.symbol in self.positions:
            # Case 1: Position already exists
            existing_position = self.positions[position.symbol]
            if existing_position.position_type == position.position_type:
                # Case 1a: Combine positions
                combined_quantity = existing_position.quantity + position.quantity
                combined_price = (
                    (existing_position.quantity * existing_position.price)
                    + (position.quantity * position.price)
                ) / combined_quantity
                existing_position.quantity = combined_quantity
                existing_position.price = combined_price
            else:
                # Case 1b: Subtract positions
                if existing_position.quantity > position.quantity:
                    existing_position.quantity -= position.quantity
                    if existing_position.quantity == 0:
                        del self.positions[position.symbol]
                else:
                    position.quantity -= existing_position.quantity
                    position.price = existing_position.price
                    self.positions[position.symbol] = position
                    if position.quantity == 0:
                        del self.positions[position.symbol]
        else:
            self.positions[position.symbol] = position
            # print(f"\tAdded new position: {position}.")
            return True

    def print_portfolio(self):
        print("Portfolio:")
        for symbol, position in self.positions.items():
            print(
                f"\t{symbol}: {position.position_type} {position.quantity} @ {position.price}"
            )
        print(f"\tCash: {self.cash}")

    def print_cash(self):
        print(f"\tCash: {self.cash}")

    def print_total_balance(self, current_data: pd.DataFrame):
        # balance = self.cash
        best_balance = self.cash
        worst_balance = self.cash
        close_balance = self.cash
        # best
        # worst
        # close
        for symbol, position in self.positions.items():
            if position.position_type == PositionType.LONG:
                close_price = current_data.loc[(symbol,), "close"].iloc[0]
                best_price = current_data.loc[(symbol,), "high"].iloc[0]
                worst_price = current_data.loc[(symbol,), "low"].iloc[0]
                best_balance += position.quantity * best_price
                worst_balance += position.quantity * worst_price
                close_balance += position.quantity * close_price
            else:
                close_price = current_data.loc[(symbol,), "close"].iloc[0]
                best_price = current_data.loc[(symbol,), "low"].iloc[0]
                worst_price = current_data.loc[(symbol,), "high"].iloc[0]
                best_balance -= position.quantity * best_price
                worst_balance -= position.quantity * worst_price
                close_balance -= position.quantity * close_price
        print(
            f"Best Balance: {best_balance}",
            f"Worst Balance: {worst_balance}",
            f"Close Balance: {close_balance}",
        )
