import unittest
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account = Account("12345", 1000.00)

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, 1000.00)

    def test_deposit_valid(self):
        self.account.deposit(500.00)
        self.assertEqual(self.account.balance, 1500.00)

    def test_deposit_invalid(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-100.00)

    def test_withdraw_valid(self):
        self.account.withdraw(300.00)
        self.assertEqual(self.account.balance, 700.00)

    def test_withdraw_invalid(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(1200.00)

    def test_withdraw_negative(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(-100.00)

    def test_buy_shares_valid(self):
        self.account.buy_shares("AAPL", 2)
        self.assertEqual(self.account.holdings["AAPL"], 2)
        self.assertEqual(self.account.balance, 700.00)

    def test_buy_shares_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", 10)

    def test_buy_shares_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -1)

    def test_sell_shares_valid(self):
        self.account.buy_shares("AAPL", 2)
        self.account.sell_shares("AAPL", 1)
        self.assertEqual(self.account.holdings["AAPL"], 1)
        self.assertEqual(self.account.balance, 850.00)

    def test_sell_shares_insufficient_quantity(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 1)

    def test_sell_shares_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -1)

    def test_calculate_portfolio_value(self):
        self.account.deposit(500.00)
        self.account.buy_shares("AAPL", 2)
        self.assertEqual(self.account.calculate_portfolio_value(), 700.00 + (150.00 * 2))

    def test_calculate_profit_or_loss(self):
        self.account.deposit(500.00)
        self.account.buy_shares("AAPL", 2)
        self.assertEqual(self.account.calculate_profit_or_loss(), (700.00 + (150.00 * 2)) - 1000.00)

    def test_list_holdings(self):
        self.account.buy_shares("AAPL", 2)
        self.assertEqual(self.account.list_holdings(), {"AAPL": 2})

    def test_list_transactions(self):
        self.account.deposit(200.00)
        self.assertIn("Deposited: 200.0", self.account.list_transactions())
        self.account.withdraw(100.00)
        self.assertIn("Withdrew: 100.0", self.account.list_transactions())
        self.account.buy_shares("AAPL", 1)
        self.assertIn("Bought: 1 shares of AAPL at 150.0 each", self.account.list_transactions())

if __name__ == '__main__':
    unittest.main()