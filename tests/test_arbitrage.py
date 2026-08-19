import unittest
from unittest.mock import MagicMock, patch
from arbitrage import find_opportunities


class TestArbitrage(unittest.TestCase):
    @patch("arbitrage.fetch_best_prices")
    def test_find_opportunities_detects_spread(self, mock_fetch_best_prices):
        # Mock exchange instances
        mock_ex1 = MagicMock()
        mock_ex2 = MagicMock()
        exchanges = {"binance": mock_ex1, "kraken": mock_ex2}

        # Setup mock returns for fetch_best_prices
        def side_effect(exchange, symbol):
            if exchange == mock_ex1:
                return {"bid": 50000.0, "ask": 50000.0}
            elif exchange == mock_ex2:
                # Sell on kraken at 51000, buy on binance at 50000 -> 2% spread
                return {"bid": 51000.0, "ask": 51000.0}
            return None

        mock_fetch_best_prices.side_effect = side_effect

        opportunities = find_opportunities(exchanges, ["BTC/USDT"])

        self.assertEqual(len(opportunities), 1)
        opp = opportunities[0]
        self.assertEqual(opp["symbol"], "BTC/USDT")
        self.assertEqual(opp["buy_exchange"], "binance")
        self.assertEqual(opp["sell_exchange"], "kraken")
        self.assertEqual(opp["buy_price"], 50000.0)
        self.assertEqual(opp["sell_price"], 51000.0)
        self.assertGreater(opp["net_spread_pct"], 0)


if __name__ == "__main__":
    unittest.main()
