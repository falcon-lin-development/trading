import unittest
from models.mock_trading.portfolio import Position, Portfolio, PositionType

class TestPortfolio(unittest.TestCase):
    def test_add_cash(self):
        portfolio = Portfolio(1000)
        portfolio.add_cash(500)
        self.assertEqual(portfolio.cash, 1500)

    def test_remove_cash_sufficient_funds(self):
        portfolio = Portfolio(1000)
        portfolio.remove_cash(500)
        self.assertEqual(portfolio.cash, 500)

    def test_remove_cash_insufficient_funds(self):
        portfolio = Portfolio(1000)
        with self.assertRaises(ValueError):
            portfolio.remove_cash(1500)

    def test_add_new_position(self):
        portfolio = Portfolio(1000)
        position = Position(PositionType.LONG, 'AAPL', 5, 100, '2024-02-10')
        transaction_commission_rate = 0.01  # 1%
        portfolio.add_position(position, transaction_commission_rate)
        self.assertIn('AAPL', portfolio.positions)
        self.assertEqual(portfolio.positions['AAPL'].quantity, 5)

    def test_combine_same_position(self):
        portfolio = Portfolio(10000)
        position1 = Position(PositionType.LONG, 'AAPL', 5, 100, '2024-02-10')
        position2 = Position(PositionType.LONG, 'AAPL', 10, 110, '2024-02-11')
        transaction_commission_rate = 0.01
        portfolio.add_position(position1, transaction_commission_rate)
        portfolio.add_position(position2, transaction_commission_rate)
        self.assertEqual(portfolio.positions['AAPL'].quantity, 15)
        self.assertAlmostEqual(portfolio.positions['AAPL'].price, 106.67, places=2)

    def test_subtract_opposite_position(self):
        portfolio = Portfolio(10000)
        position1 = Position(PositionType.LONG, 'AAPL', 10, 100, '2024-02-10')
        position2 = Position(PositionType.SHORT, 'AAPL', 5, 110, '2024-02-11')
        transaction_commission_rate = 0.01
        portfolio.add_position(position1, transaction_commission_rate)
        portfolio.add_position(position2, transaction_commission_rate)
        self.assertEqual(portfolio.positions['AAPL'].quantity, 5)
        self.assertEqual(portfolio.positions['AAPL'].position_type, PositionType.LONG)

if __name__ == '__main__':
    unittest.main()
