"""
Gère la connexion aux exchanges via CCXT et la récupération des order books.
"""
import ccxt
import logging
from config import EXCHANGES

logger = logging.getLogger(__name__)


def init_exchanges() -> dict:
    """Initialise les objets ccxt pour chaque exchange configuré."""
    instances = {}
    for name, creds in EXCHANGES.items():
        try:
            exchange_class = getattr(ccxt, name)
            instances[name] = exchange_class({
                "apiKey": creds.get("api_key", ""),
                "secret": creds.get("secret", ""),
                "password": creds.get("password", ""),  # requis par certains (ex: kucoin)
                "enableRateLimit": True,
            })
            logger.info(f"Exchange initialisé : {name}")
        except Exception as e:
            logger.error(f"Erreur init {name}: {e}")
    return instances


def fetch_best_prices(exchange, symbol: str):
    """
    Récupère le meilleur bid (vente) et ask (achat) pour une paire donnée.
    Retourne None si le symbole n'est pas supporté ou en cas d'erreur réseau.
    """
    try:
        order_book = exchange.fetch_order_book(symbol)
        best_bid = order_book["bids"][0][0] if order_book["bids"] else None
        best_ask = order_book["asks"][0][0] if order_book["asks"] else None
        return {"bid": best_bid, "ask": best_ask}
    except ccxt.BadSymbol:
        return None
    except Exception as e:
        logger.warning(f"Erreur fetch {symbol} sur {exchange.id}: {e}")
        return None
