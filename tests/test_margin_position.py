import unittest
from decimal import Decimal

# Assuming MarginPosition class is imported from the margin_position module
from models.backtesting.marginPosition import MarginPosition, Decimal

class TestMarginPosition(unittest.TestCase):
    def setUp(self):
        # Set up a MarginPosition instance for testing
        self.position_long = MarginPosition(
            symbol="BTC",
            entry_price="50000",
            equity="10000",
            side=MarginPosition.Side.LONG,
            leverage=10
        )
        self.position_short = MarginPosition(
            symbol="BTC",
            entry_price="50000",
            equity="10000",
            side=MarginPosition.Side.SHORT,
            leverage=10
        )
        self.current_price = Decimal("45000")

    def test_pnl_long(self):
        # Test profit and loss for a long position
        expected_pnl = Decimal("-10000")  # Calculated manually for test verification
        self.assertEqual(self.position_long.pnl(self.current_price), expected_pnl)

    def test_pnl_short(self):
        # Test profit and loss for a short position
        expected_pnl = Decimal("10000")  # Calculated manually for test verification
        self.assertEqual(self.position_short.pnl(self.current_price), expected_pnl)

    def test_pnl_percentage(self):
        # Test P&L percentage calculation
        expected_percentage = Decimal("100.0")  # Calculated manually for test verification
        self.assertEqual(self.position_short.pnl_percentage(self.current_price), expected_percentage)

    def test_liquidation_price_long(self):
        # Test liquidation price for a long position
        expected_liquidation_price = Decimal("45000")  # Calculated manually
        self.assertEqual(self.position_long.liquidation_price(), expected_liquidation_price)

    def test_liquidation_price_short(self):
        # Test liquidation price for a short position
        expected_liquidation_price = Decimal("55000")  # Calculated manually
        self.assertEqual(self.position_short.liquidation_price(), expected_liquidation_price)

    def test_position_value(self):
        # Test the market value of the position
        expected_value = Decimal("90000")  # Calculated manually
        self.assertEqual(self.position_short.position_value(self.current_price), expected_value)

    def test_short_position_evaluation(self):
        # Test the net amount received or paid when unwinding the position
        expected_evaluation = Decimal("20000")  # Calculated manually
        self.assertEqual(self.position_short.position_evaluation(self.current_price), expected_evaluation)

    def test_long_position_evaluation(self):
        # Test the net amount received or paid when unwinding the position
        expected_evaluation = Decimal("0")  # Calculated manually
        self.assertEqual(self.position_long.position_evaluation(self.current_price), expected_evaluation)

if __name__ == '__main__':
    unittest.main()
