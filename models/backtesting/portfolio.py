from decimal import Decimal
import pandas as pd
from enum import Enum
from .marginPosition import MarginPosition
from .strategy import Action
import pprint

def calculate_drawdowns(portfolio_history):
    portfolio_history = portfolio_history.copy()
    portfolio_history['min_portfolio_value'] = portfolio_history[['close', 'open', 'high', 'low']].min(axis=1)
    portfolio_history['max_portfolio_value'] = portfolio_history[['close', 'open', 'high', 'low']].max(axis=1)
    portfolio_history["max_drawdown"] = (
        portfolio_history["close"] - portfolio_history["max_portfolio_value"].cummax()
    )
    portfolio_history["max_drawdown_percentage"] = (
        (portfolio_history["close"] - portfolio_history["max_portfolio_value"].cummax())  / portfolio_history["max_portfolio_value"].cummax() * 100 
    )
    portfolio_history["max_return_percentage"] = (
        (portfolio_history["close"] - portfolio_history["max_portfolio_value"].cummin()) / portfolio_history["min_portfolio_value"].cummin() * 100
    )
    # calculate 0 based return, meaning the return against the first closed value
    portfolio_history["0-based_return"] = (
        (portfolio_history["close"] - portfolio_history["close"].iloc[0]) / portfolio_history["close"].iloc[0] * 100
    )

    return portfolio_history


class Transaction:
    class Side(Enum):
        OPEN_LONG = 1
        CLOSE_LONG = 2
        OPEN_SHORT = 3
        CLOSE_SHORT = 4

    def __init__(self, symbol, quantity, price, date, side=None, leverage=1):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.date = date
        self.side = side
        self.leverage = leverage


class Portfolio:
    def __init__(self, initial_capital=0):
        self.is_end = False
        self.cash = initial_capital
        self.holdings = {}

        self.transactions = []
        self.portfolio_history = pd.DataFrame(
            columns=["datetime", "open", "high", "low", "close", "cash"]
        )

    def long(self, symbol, equity, price, date, leverage=1.0):
        """
        If No/Long Position, buy
        If Short Position, unwind
        """
        try:
            _action = None
            _position = None

            # step 1: determine the current position
            if not symbol in self.holdings:
                self.holdings[symbol] = []

            # step 2b: if current position, if same side, open position, else, close position
            for position in self.holdings[symbol][:]:
                if position.side == MarginPosition.Side.SHORT:
                    self.holdings[symbol].remove(position)
                    self.cash += position.position_evaluation(price)
                    self.transactions.append(
                        Transaction(
                            symbol=symbol,
                            quantity=position.size,
                            price=price,
                            date=date,
                            side=Transaction.Side.CLOSE_SHORT,
                            leverage=position.leverage,
                        )
                    )
                    ### RETURN VALUES ###
                    _position = position
                    _action = Transaction.Side.CLOSE_SHORT
                    ### RETURN VALUES ###

                    break
            else:
                # step 2a: if no current position, open poistion
                position = MarginPosition(
                    symbol=symbol,
                    entry_price=price,
                    equity=equity,
                    side=MarginPosition.Side.LONG,
                    leverage=leverage,
                )

                ### RETURN VALUES ###
                _position = position  # set return value
                if equity > self.cash:
                    raise ValueError("Not enough cash to buy. skipping transaction.")
                _action = Transaction.Side.OPEN_LONG
                ### RETURN VALUES ###

                self.cash -= equity
                self.holdings[symbol].append(position)
                self.transactions.append(
                    Transaction(
                        symbol=symbol,
                        quantity=position.size,
                        price=price,
                        date=date,
                        side=Transaction.Side.OPEN_LONG,
                        leverage=position.leverage,
                    )
                )

            return _action, _position
        except ValueError as e:
            print(e)
            return _action, _position

    def short(self, symbol, equity, price, date, leverage=1.0):
        """
        If No/Short Position, short
        If Long Position, unwind
        """
        try:
            _action = None
            _position = None

            # step 1: determine the current position
            if not symbol in self.holdings:
                self.holdings[symbol] = []

            # step 2b: if current position, if same side, open position, else, close position
            for position in self.holdings[symbol][:]:
                if position.side == MarginPosition.Side.LONG:
                    self.holdings[symbol].remove(position)
                    self.cash += position.position_evaluation(price)
                    self.transactions.append(
                        Transaction(
                            symbol=symbol,
                            quantity=position.size,
                            price=price,
                            date=date,
                            side=Transaction.Side.CLOSE_LONG,
                            leverage=position.leverage,
                        )
                    )

                    ### RETURN VALUES ###
                    _position = position
                    _action = Transaction.Side.CLOSE_LONG
                    ### RETURN VALUES ###
                    break
            else:
                # step 2a: if no current position, open poistion
                position = MarginPosition(
                    symbol=symbol,
                    entry_price=price,
                    equity=equity,
                    side=MarginPosition.Side.SHORT,
                    leverage=leverage,
                )

                ### RETURN VALUES ###
                _position = position  # set return value
                if equity > self.cash:
                    raise ValueError("Not enough cash to buy. skipping transaction.")
                _action = Transaction.Side.OPEN_SHORT
                ### RETURN VALUES ###

                self.cash -= equity  # equity is needed even to short
                self.holdings[symbol].append(position)
                self.transactions.append(
                    Transaction(
                        symbol=symbol,
                        quantity=position.size,
                        price=price,
                        date=date,
                        side=Transaction.Side.OPEN_SHORT,
                        leverage=position.leverage,
                    )
                )

            return _action, _position
        except ValueError as e:
            print(e)
            return _action, _position

    def evaluate_portfolio(self, current_row: pd.DataFrame, verbose=True):
        """
        Evaluate the portfolio at the current time, evalute by open, high, low, close
        """
        o, h, l, c = 0, 0, 0, 0
        # start with self.cash
        for symbol, position_list in self.holdings.items():
            for position in position_list:
                o += position.position_evaluation(
                    current_price=current_row.loc[
                        current_row["symbol"] == symbol, "open"
                    ].values[0]
                )
                h += position.position_evaluation(
                    current_price=current_row.loc[
                        current_row["symbol"] == symbol, "high"
                    ].values[0]
                )
                l += position.position_evaluation(
                    current_price=current_row.loc[
                        current_row["symbol"] == symbol, "low"
                    ].values[0]
                )
                c += position.position_evaluation(
                    current_price=current_row.loc[
                        current_row["symbol"] == symbol, "close"
                    ].values[0]
                )
                # if verbose:
                #     print(position)
                #     current_price = current_row.loc[
                #         current_row["symbol"] == symbol, "close"
                #     ].values[0]
                #     print(
                #         "Current: ",
                #         current_price,
                #         "Earning: ",
                #         position.position_evaluation(current_price),
                #     )

        self.portfolio_history = pd.concat(
            [
                self.portfolio_history,
                pd.DataFrame(
                    [
                        {
                            "datetime": current_row["datetime"].values[0],
                            "open": o + self.cash,
                            "high": h + self.cash,
                            "low": l + self.cash,
                            "close": c + self.cash,
                            "cash": self.cash,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        return self.portfolio_history

    def clean_up(self, current_row: pd.DataFrame):
        """
        Clean up the portfolio at each iteration
        """
        liquidate_percentage = 1
        history = pd.DataFrame(
            columns=[
                "datetime",
                "symbol",
                "action",
                "price",
                "quantity",
            ]
        )
        for symbol, position_list in self.holdings.items():
            for position in position_list[:]:
                v = position.position_evaluation(
                    current_row.loc[current_row["symbol"] == symbol, "close"].values[0]
                )
                if v <= 0:
                    self.holdings[symbol].remove(position)
                    self.cash += v
                    self.transactions.append(
                        Transaction(
                            symbol=symbol,
                            quantity=position.size,
                            price=current_row.loc[
                                current_row["symbol"] == symbol, "close"
                            ].values[0],
                            date=current_row["datetime"].values[0],
                            side=(
                                Transaction.Side.CLOSE_LONG
                                if position.side == MarginPosition.Side.LONG
                                else Transaction.Side.CLOSE_SHORT
                            ),
                        )
                    )
                    history = pd.concat(
                        [
                            history,
                            pd.DataFrame(
                                {
                                    "datetime": current_row["datetime"].values[0],
                                    "symbol": symbol,
                                    "action": Action.FORCE_LIQUITATION,
                                    "price": current_row.loc[
                                        current_row["symbol"] == symbol, "close"
                                    ].values[0],
                                    "quantity": position.size,
                                },
                                index=[0],
                            ),
                        ],
                        ignore_index=True,
                    )
                    print(
                        "clean up position: ",
                        position.side,
                        position.size,
                    )

    def info(self):
        """
            Print the portfolio information
            -> Start Time
            -> Cash
            -> Holdings
            -> Evaluation
            -> PNL ( + Percentage )
            -> End Time
            -> Max DrawDown Percentage
            -> Max Return Percentage
        """
        print("Start Time: ", self.portfolio_history["datetime"].iloc[0])
        print("End Time: ", self.portfolio_history["datetime"].iloc[-1])
        print("Cash: ", self.cash)
        print("Holdings: ")
        pprint.pprint(self.holdings)
        print("Evaluation: ", self.portfolio_history["close"].iloc[-1])
        print("PNL: ", self.portfolio_history["close"].iloc[-1] - self.portfolio_history["close"].iloc[0])
        print(
            "PNL Percentage: ",
            (
                self.portfolio_history["close"].iloc[-1]
                - self.portfolio_history["close"].iloc[0]
            )
            / self.portfolio_history["close"].iloc[0]
            * 100,
        )
        print(
            "Max DrawDown Percentage: ",
            self.portfolio_history["max_drawdown_percentage"].min(),
        )
        print(
            "Max Return Percentage: ",
            self.portfolio_history["max_return_percentage"].max(),
        )

    def end(self):
        self.is_end = True
        self.portfolio_history = calculate_drawdowns(self.portfolio_history)