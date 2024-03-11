class MockTradingAPI:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.portfolio = {}  # Stores symbol: quantity pairs
        self.slippage_rate = 0.003  # 0.3% slippage
        self.transaction_cost = 0.00025  # 0.025%

    def get_market_price(self, symbol):
        # Simplified method to get current market price for a symbol
        # In a real scenario, this would fetch live data or simulate market conditions
        prices = {
            'BTC': 50000,
            'ETH': 4000,
            # Add more symbols and prices as needed
        }
        return prices.get(symbol, None)
    
    def calculate_slippage(self, order_size, market_price):
        # Simulate slippage based on order size and market price
        # This is simplified; real slippage depends on liquidity and other factors
        slippage = market_price * self.slippage_rate
        return slippage

    def place_order(self, symbol, quantity):
        market_price = self.get_market_price(symbol)
        if market_price is None:
            print(f"Symbol {symbol} not found.")
            return False
        
        order_cost = market_price * quantity
        slippage = self.calculate_slippage(order_cost, market_price)
        total_cost = order_cost + slippage + (order_cost * self.transaction_cost)

        if total_cost > self.cash:
            print("Insufficient funds to complete the order.")
            return False
        
        self.cash -= total_cost
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
        print(f"Order placed for {quantity} of {symbol} at price {market_price}, total cost {total_cost}.")
        return True

    def print_portfolio(self):
        print("Portfolio:", self.portfolio)
        print("Cash remaining:", self.cash)

# Example usage
api = MockTradingAPI(initial_cash=100000)
api.place_order('BTC', 1)  # Attempt to buy 1 BTC
api.place_order('ETH', 10)  # Attempt to buy 10 ETH
api.print_portfolio()
