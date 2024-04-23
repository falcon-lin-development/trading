import pandas as pd
import numpy as np
from enum import Enum


import plotly.graph_objects as go
from plotly.subplots import make_subplots



class Action(Enum):
    """Enum for the action to take."""

    LONG = 1
    LONG_UNWIND = 2
    MISSED_LONG = 3

    SHORT = 4
    SHORT_UNWIND = 5
    MISSED_SHORT = 6

    HOLD = 7
    FORCE_LIQUITATION = 8



def _plotly_portfolio(portfolio_history):
    portfolio_history = portfolio_history.copy()
    if not isinstance(portfolio_history.index, pd.DatetimeIndex):
        portfolio_history.set_index("datetime", inplace=True)

    fig = make_subplots(
        rows=6,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=(
            "Portfolio",
            "Cash",
            "Max Drawdown",
            "Max Drawdown %",
            "Max Return %" ,
            "0-Based Return %",
        ),
        row_width=[ 0.3, 0.3, 0.3, 0.3, 0.2, 0.2],
    )

    # portfolio value
    for i in range(4):
        cols = [
            "open",
            "high",
            "low",
            "close",
        ]
        colors = ["blue", "green", "red", "purple"]
        fig.add_trace(
            go.Scatter(
                x=portfolio_history.index,
                y=portfolio_history[cols[i]],
                mode="lines",
                name=f"Portfolio {cols[i]}Value",
                line=dict(color=colors[i], width=2),
            ),
            row=1,
            col=1,
        )

    # cash
    fig.add_trace(
        go.Scatter(
            x=portfolio_history.index,
            y=portfolio_history["cash"],
            mode="lines",
            name="Cash",
            line=dict(color="black", width=2),
        ),
        row=2,
        col=1,
    )

    # max drawdown
    fig.add_trace(
        go.Scatter(
            x=portfolio_history.index,
            y=portfolio_history["max_drawdown"],
            mode="lines",
            name="Max Drawdown",
            line=dict(color="red", width=2),
        ),
        row=3,
        col=1,
    )

    # max drawdown percentage
    fig.add_trace(
        go.Scatter(
            x=portfolio_history.index,
            y=portfolio_history["max_drawdown_percentage"],
            mode="lines",
            name="Max Drawdown Percentage",
            line=dict(color="red", width=2),
        ),
        row=4,
        col=1,
    )

    # max return percentage
    fig.add_trace(
        go.Scatter(
            x=portfolio_history.index,
            y=portfolio_history["max_return_percentage"],
            mode="lines",
            name="Max Return Percentage",
            line=dict(color="green", width=2),
        ),
        row=5,
        col=1,
    )

    # 0 based return
    fig.add_trace(
        go.Scatter(
            x=portfolio_history.index,
            y=portfolio_history["0-based_return"],
            mode="lines",
            name="0-Based Return",
            line=dict(color="blue", width=2),
        ),
        row=6,
        col=1,
    )


    fig.update_layout(
        height=1000,

        title="Portfolio Value",
        xaxis_title="Date",
        yaxis_title="Value",
        xaxis_rangeslider_visible=False,
    )
    fig.update_xaxes(rangeslider_visible=True, row=6, col=1)
    fig.show()


def _plotly_strategy(data, history, portfolio_history):
    """
    Use Plotly to create an interactive plot of OHLCV data with Bollinger Bands
    and overlays of buy/sell markers based on the history DataFrame.
    """
    # fix data
    data = data.copy()
    history = history.copy()
    portfolio_history = portfolio_history.copy()
    if not isinstance(data.index, pd.DatetimeIndex):
        data.set_index("datetime", inplace=True)
    if not isinstance(history.index, pd.DatetimeIndex):
        history.set_index("datetime", inplace=True)
    if not isinstance(portfolio_history.index, pd.DatetimeIndex):
        portfolio_history.set_index("datetime", inplace=True)

    # Create the figure
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=("Candlestick", "Cash", "Portfolio Value"),
        row_width=[0.2, 0.2, 0.6],
    )

    # Add Bollinger Bands
    # Create the Candlestick chart +
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            name="OHLC",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Upper Band"],
            line=dict(color="black", width=1),
            name="Upper Band",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Middle Band"],
            line=dict(color="black", width=1),
            name="Middle Band",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Lower Band"],
            line=dict(color="black", width=1),
            name="Lower Band",
        )
    )

    # Add Buy markers
    ### Buys ###
    buys = history[history["action"] == Action.LONG]
    buys = buys[buys.index.isin(data.index)]
    fig.add_trace(
        go.Scatter(
            x=buys.index,
            y=buys["price"],
            mode="markers",
            marker=dict(color="green", size=10, symbol="triangle-up"),
            name="Buy",
        )
    )
    ### Short Unwind ###
    short_unwind = history[history["action"] == Action.SHORT_UNWIND]
    short_unwind = short_unwind[
        short_unwind.index.isin(data.index)
    ]  # Ensure the buy markers are within the data range
    fig.add_trace(
        go.Scatter(
            x=short_unwind.index,
            y=short_unwind["price"],
            mode="markers",
            marker=dict(color="blue", size=10, symbol="triangle-up"),
            name="Short Unwind",
        )
    )
    ### Missed Long ###
    missed_long = history[history["action"] == Action.MISSED_LONG]
    missed_long = missed_long[
        missed_long.index.isin(data.index)
    ]  # Ensure the buy markers are within the data range
    fig.add_trace(
        go.Scatter(
            x=missed_long.index,
            y=missed_long["price"],
            mode="markers",
            marker=dict(color="black", size=10, symbol="triangle-up"),
            name="Missed Long",
        )
    )

    # Add Sell markers
    ### Sells ###
    sells = history[history["action"] == Action.SHORT]
    sells = sells[
        sells.index.isin(data.index)
    ]  # Ensure the sell markers are within the data range
    fig.add_trace(
        go.Scatter(
            x=sells.index,
            y=sells["price"],
            mode="markers",
            marker=dict(color="red", size=10, symbol="triangle-down"),
            name="Sell",
        )
    )
    ### Long Unwind ###
    long_unwind = history[history["action"] == Action.LONG_UNWIND]
    long_unwind = long_unwind[
        long_unwind.index.isin(data.index)
    ]  # Ensure the sell markers are within the data range
    fig.add_trace(
        go.Scatter(
            x=long_unwind.index,
            y=long_unwind["price"],
            mode="markers",
            marker=dict(color="yellow", size=10, symbol="triangle-down"),
            name="Long Unwind",
        )
    )
    ### Missed Short ###
    missed_short = history[history["action"] == Action.MISSED_SHORT]
    missed_short = missed_short[
        missed_short.index.isin(data.index)
    ]  # Ensure the sell markers are within the data range
    fig.add_trace(
        go.Scatter(
            x=missed_short.index,
            y=missed_short["price"],
            mode="markers",
            marker=dict(color="black", size=10, symbol="triangle-down"),
            name="Missed Short",
        )
    )

    ######### FORCE UNWIND ############
    force_unwind = history[history["action"] == Action.FORCE_LIQUITATION]
    force_unwind = force_unwind[
        force_unwind.index.isin(data.index)
    ]  # Ensure the sell markers are within the data range
    fig.add_trace(
        go.Scatter(
            x=force_unwind.index,
            y=force_unwind["price"],
            mode="markers",
            marker=dict(color="red", size=10, symbol="x"),
            name="Force Unwind",
        )
    )

    ########### Graph 2 ###########
    # Volume bars
    # fig.add_trace(
    #     go.Bar(x=data.index, y=data["volume"], name="Volume", marker_color="blue"),
    #     row=2,
    #     col=1,
    # )
    # cash
    fig.add_trace(
        go.Scatter(
            x=portfolio_history.index,
            y=portfolio_history["cash"],
            mode="lines",
            name="Cash",
            line=dict(color="yellow", width=2),
        ),
        row=2,
        col=1,
    )

    ########### Graph 3 ###########
    # Create the Portfolio chart
    for i in range(4):
        cols = [
            "open",
            "high",
            "low",
            "close",
        ]
        colors = ["blue", "green", "red", "purple"]
        fig.add_trace(
            go.Scatter(
                x=portfolio_history.index,
                y=portfolio_history[cols[i]],
                mode="lines",
                name=f"Portfolio {cols[i]}Value",
                line=dict(color=colors[i], width=2),
            ),
            row=3,
            col=1,
        )

    # Update layout for a more detailed view
    fig.update_layout(
        title="Bollinger Bands Strategy Plot",
        yaxis_title="Price",
        xaxis_title="Date",
        # width=1300,  # Set the width of the plot
        height=1000,  # Set the height of the plot
        xaxis_rangeslider_visible=False,
    )  # Disable range slider for more space

    # Make x-axis range sliders visible only for the bottom plot
    fig.update_xaxes(rangeslider_visible=True, row=3, col=1)

    fig.show()


class Strategy:
    """
    Now focus on a single symbol, in the future will support multiple symbols
    """

    @staticmethod
    def plotly_portfolio(portfolio_history):
        _plotly_portfolio(portfolio_history)

    @staticmethod
    def plotly_strategy(data, history, portfolio_history):
        _plotly_strategy(data, history, portfolio_history)

    def run(self, current_data, historical_data):
        """
        this strategy takes in the current portfolio and past data to execute trades
        """
        raise NotImplementedError("run() method must be implemented by the subclass.")

    def plot_history(self):
        """
        this method will plot the action history of the strategy
        """
        raise NotImplementedError(
            "plot_history() method must be implemented by the subclass."
        )

    def plot_performance(self):
        """
        this method will plot the performance of the strategy
        """
        raise NotImplementedError(
            "plot_performance() method must be implemented by the subclass."
        )

    def plot_trades(self):
        """
        this method will plot the trades of the strategy
        """
        raise NotImplementedError(
            "plot_trades() method must be implemented by the subclass."
        )
