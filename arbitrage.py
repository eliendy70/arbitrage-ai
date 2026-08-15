"""
Compare les prix entre exchanges et détecte les opportunités d'arbitrage
rentables après déduction des frais estimés.
"""
from itertools import combinations
from config import MIN_SPREAD_PERCENT, TAKER_FEE_ESTIMATE
from exchanges import fetch_best_prices


def find_opportunities(exchange_instances: dict, symbols: list) -> list:
    """
    Pour chaque paire de symbole, compare tous les exchanges entre eux
    et retourne les opportunités dont le spread net dépasse le seuil.
    """
    opportunities = []

    for symbol in symbols:
        prices = {}
        for name, exchange in exchange_instances.items():
            result = fetch_best_prices(exchange, symbol)
            if result and result["bid"] and result["ask"]:
                prices[name] = result

        # Compare chaque paire d'exchanges (achat sur l'un, vente sur l'autre)
        for buy_ex, sell_ex in combinations(prices.keys(), 2):
            for a, b in [(buy_ex, sell_ex), (sell_ex, buy_ex)]:
                buy_price = prices[a]["ask"]   # prix pour ACHETER sur l'exchange a
                sell_price = prices[b]["bid"]  # prix pour VENDRE sur l'exchange b

                if buy_price <= 0:
                    continue

                gross_spread_pct = ((sell_price - buy_price) / buy_price) * 100
                # Déduit les frais des deux côtés (achat + vente)
                net_spread_pct = gross_spread_pct - (2 * TAKER_FEE_ESTIMATE)

                if net_spread_pct >= MIN_SPREAD_PERCENT:
                    opportunities.append({
                        "symbol": symbol,
                        "buy_exchange": a,
                        "sell_exchange": b,
                        "buy_price": buy_price,
                        "sell_price": sell_price,
                        "gross_spread_pct": round(gross_spread_pct, 3),
                        "net_spread_pct": round(net_spread_pct, 3),
                    })

    return opportunities
