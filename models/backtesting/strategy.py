import pandas as pd
import numpy as np
from enum import Enum


class Strategy:
    """
        Now focus on a single symbol, in the future will support multiple symbols
    """

    def run(self, current_data, historical_data):
        """
        this strategy takes in the current portfolio and past data to execute trades
        """
        raise NotImplementedError("run() method must be implemented by the subclass.")

    def plot_history(self):
        """
        this method will plot the action history of the strategy
        """
        raise NotImplementedError("plot_history() method must be implemented by the subclass.")

    def plot_performance(self):
        """
        this method will plot the performance of the strategy
        """
        raise NotImplementedError("plot_performance() method must be implemented by the subclass.")

    def plot_trades(self):
        """
        this method will plot the trades of the strategy
        """
        raise NotImplementedError("plot_trades() method must be implemented by the subclass.")


