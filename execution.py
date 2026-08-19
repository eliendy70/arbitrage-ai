"""
Module d'exécution des trades d'arbitrage (simulation et mode réel).
"""
import logging
from config import TRADE_AMOUNT_USDT, PAPER_TRADING, TAKER_FEE_ESTIMATE

logger = logging.getLogger(__name__)


def check_liquidity(exchange, symbol: str, required_amount_usdt: float, side: str) -> bool:
    """
    Vérifie la profondeur du carnet d'ordres pour s'assurer que le montant demandé
    peut être absorbé par le marché.
    side: 'ask' pour achat, 'bid' pour vente.
    """
    try:
        order_book = exchange.fetch_order_book(symbol)
        entries = order_book["asks"] if side == "ask" else order_book["bids"]
        accumulated_usdt = 0.0

        for price, amount in entries:
            accumulated_usdt += price * amount
            if accumulated_usdt >= required_amount_usdt:
                return True
        return False
    except Exception as e:
        logger.error(f"Erreur vérification liquidité sur {exchange.id} pour {symbol}: {e}")
        return False


def execute_arbitrage_trade(opp: dict, exchange_instances: dict) -> dict:
    """
    Exécute un trade d'arbitrage en fonction de l'opportunité détectée.
    Retourne un dictionnaire résumant l'exécution (succès, prix, profit).
    """
    buy_ex_name = opp["buy_exchange"]
    sell_ex_name = opp["sell_exchange"]
    symbol = opp["symbol"]

    buy_ex = exchange_instances.get(buy_ex_name)
    sell_ex = exchange_instances.get(sell_ex_name)

    if not buy_ex or not sell_ex:
        logger.error(f"Exchange non initialisé: buy_ex={buy_ex_name}, sell_ex={sell_ex_name}")
        return {"status": "failed", "reason": "Exchange instance missing"}

    amount_usdt = TRADE_AMOUNT_USDT
    estimated_buy_price = opp["buy_price"]
    estimated_sell_price = opp["sell_price"]

    # Calcul de la quantité de base (ex: BTC, ETH) à échanger
    crypto_amount = amount_usdt / estimated_buy_price

    if PAPER_TRADING:
        logger.info(
            f"[PAPER TRADING] Exécution simulée d'arbitrage pour {symbol}:\n"
            f"  Achat: {crypto_amount:.6f} {symbol.split('/')[0]} sur {buy_ex_name} à {estimated_buy_price}\n"
            f"  Vente: {crypto_amount:.6f} {symbol.split('/')[0]} sur {sell_ex_name} à {estimated_sell_price}"
        )

        gross_profit = (estimated_sell_price - estimated_buy_price) * crypto_amount
        fees = (amount_usdt * (TAKER_FEE_ESTIMATE / 100)) * 2
        net_profit = gross_profit - fees

        return {
            "status": "success",
            "paper_trading": True,
            "symbol": symbol,
            "buy_exchange": buy_ex_name,
            "sell_exchange": sell_ex_name,
            "buy_price": estimated_buy_price,
            "sell_price": estimated_sell_price,
            "amount_usdt": amount_usdt,
            "crypto_amount": crypto_amount,
            "gross_profit_usdt": round(gross_profit, 4),
            "net_profit_usdt": round(net_profit, 4),
        }

    # Mode réel : vérification de liquidité
    if not check_liquidity(buy_ex, symbol, amount_usdt, side="ask"):
        logger.warning(f"Liquidité insuffisante sur {buy_ex_name} pour le symbole {symbol}")
        return {"status": "failed", "reason": f"Insufficient liquidity on {buy_ex_name}"}

    if not check_liquidity(sell_ex, symbol, amount_usdt, side="bid"):
        logger.warning(f"Liquidité insuffisante sur {sell_ex_name} pour le symbole {symbol}")
        return {"status": "failed", "reason": f"Insufficient liquidity on {sell_ex_name}"}

    try:
        logger.info(f"Passage ordre d'achat sur {buy_ex_name} pour {crypto_amount} {symbol}...")
        buy_order = buy_ex.create_market_buy_order(symbol, crypto_amount)

        logger.info(f"Passage ordre de vente sur {sell_ex_name} pour {crypto_amount} {symbol}...")
        sell_order = sell_ex.create_market_sell_order(symbol, crypto_amount)

        actual_buy_price = buy_order.get("average", estimated_buy_price)
        actual_sell_price = sell_order.get("average", estimated_sell_price)

        gross_profit = (actual_sell_price - actual_buy_price) * crypto_amount
        fees = (amount_usdt * (TAKER_FEE_ESTIMATE / 100)) * 2
        net_profit = gross_profit - fees

        return {
            "status": "success",
            "paper_trading": False,
            "symbol": symbol,
            "buy_exchange": buy_ex_name,
            "sell_exchange": sell_ex_name,
            "buy_price": actual_buy_price,
            "sell_price": actual_sell_price,
            "amount_usdt": amount_usdt,
            "crypto_amount": crypto_amount,
            "gross_profit_usdt": round(gross_profit, 4),
            "net_profit_usdt": round(net_profit, 4),
            "buy_order": buy_order,
            "sell_order": sell_order,
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution en direct des ordres d'arbitrage: {e}")
        return {"status": "failed", "reason": str(e)}
