import enum


class PositionType(enum):
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
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.positions = {}

    def add_cash(self, amount):
        self.cash += amount
        print(f"Added {amount} to cash. Total cash now {self.cash}.")

    def remove_cash(self, amount):
        if amount > self.cash:
            print("Insufficient funds.")
            raise ValueError("Insufficient funds.")
            # return False
        self.cash -= amount
        print(f"Removed {amount} from cash. Total cash now {self.cash}.")
        # return True

    def add_position(self, position, transaction_commission_rate):
        """
            Add a new position to the portfolio
            1) if position already exists, combine the positions
                -> if position is the same type, add the quantities, weighted average the price
                -> if position is the opposite type, subtract the quantities, use the price of the larger position

            2) if position does not exist, add the position to the portfolio
            
            3) if the cost of the position is greater than the cash, do not add the position
        """
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
                print(
                    f"Combined {position.symbol} positions. New quantity: {combined_quantity}, new price: {combined_price}."
                )
            else:
                # Case 1b: Subtract positions
                if existing_position.quantity > position.quantity:
                    existing_position.quantity -= position.quantity
                    print(
                        f"Subtracted {position.quantity} from {position.symbol} position. New quantity: {existing_position.quantity}."
                    )
                else:
                    position.quantity -= existing_position.quantity
                    position.price = existing_position.price
                    self.positions[position.symbol] = position
                    print(
                        f"Subtracted {existing_position.quantity} from {position.symbol} position. New quantity: {position.quantity}."
                    )
        else:
            self.positions[position.symbol] = position
            print(f"Added new position: {position}.")
            return True

    def print_portfolio(self):
        print("Portfolio:")
        for symbol, position in self.positions.items():
            print(f"{symbol}: {position.quantity} @ {position.price}")
        print(f"Cash: {self.cash}")