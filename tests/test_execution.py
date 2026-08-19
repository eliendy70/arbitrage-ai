import unittest
from unittest.mock import MagicMock, patch
import execution
from execution import execute_arbitrage_trade, check_liquidity


class TestExecution(unittest.TestCase):
    def setUp(self):
        self.opp = {
            "symbol": "BTC/USDT",
            "buy_exchange": "binance",
            "sell_exchange": "kraken",
            "buy_price": 50000.0,
            "sell_price": 51000.0,
            "gross_spread_pct": 2.0,
            "net_spread_pct": 1.8,
        }
        self.mock_binance = MagicMock()
        self.mock_binance.id = "binance"
        self.mock_kraken = MagicMock()
        self.mock_kraken.id = "kraken"
        self.exchanges = {
            "binance": self.mock_binance,
            "kraken": self.mock_kraken,
        }

    @patch("execution.PAPER_TRADING", True)
    @patch("execution.TRADE_AMOUNT_USDT", 100.0)
    def test_execute_arbitrage_trade_paper_trading(self):
        res = execute_arbitrage_trade(self.opp, self.exchanges)

        self.assertEqual(res["status"], "success")
        self.assertTrue(res["paper_trading"])
        self.assertEqual(res["amount_usdt"], 100.0)
        self.assertEqual(res["crypto_amount"], 100.0 / 50000.0)
        self.assertIn("net_profit_usdt", res)
        # Verify no orders were actually called on CCXT mocks
        self.mock_binance.create_market_buy_order.assert_not_called()
        self.mock_kraken.create_market_sell_order.assert_not_called()

    @patch("execution.PAPER_TRADING", False)
    @patch("execution.TRADE_AMOUNT_USDT", 100.0)
    @patch("execution.check_liquidity", return_value=True)
    def test_execute_arbitrage_trade_live(self, mock_liquidity):
        self.mock_binance.create_market_buy_order.return_value = {"average": 50000.0}
        self.mock_kraken.create_market_sell_order.return_value = {"average": 51000.0}

        res = execute_arbitrage_trade(self.opp, self.exchanges)

        self.assertEqual(res["status"], "success")
        self.assertFalse(res["paper_trading"])
        self.mock_binance.create_market_buy_order.assert_called_once_with("BTC/USDT", 100.0 / 50000.0)
        self.mock_kraken.create_market_sell_order.assert_called_once_with("BTC/USDT", 100.0 / 50000.0)

    def test_check_liquidity_success(self):
        self.mock_binance.fetch_order_book.return_value = {
            "asks": [[50000.0, 0.01]],  # 500 USDT value
            "bids": [[50000.0, 0.01]],
        }
        has_liquidity = check_liquidity(self.mock_binance, "BTC/USDT", 100.0, "ask")
        self.assertTrue(has_liquidity)

    def test_check_liquidity_insufficient(self):
        self.mock_binance.fetch_order_book.return_value = {
            "asks": [[50000.0, 0.0001]],  # 5 USDT value
            "bids": [[50000.0, 0.0001]],
        }
        has_liquidity = check_liquidity(self.mock_binance, "BTC/USDT", 100.0, "ask")
        self.assertFalse(has_liquidity)


if __name__ == "__main__":
    unittest.main()
