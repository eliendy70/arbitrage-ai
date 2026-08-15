"""
Envoie les alertes d'opportunités d'arbitrage sur Telegram.
"""
import logging
from telegram import Bot
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_opportunity_alert(opp: dict):
    """Formate et envoie une alerte pour une opportunité détectée."""
    message = (
        f"🔔 *Opportunité d'arbitrage détectée*\n\n"
        f"Paire : `{opp['symbol']}`\n"
        f"Acheter sur : *{opp['buy_exchange']}* à `{opp['buy_price']}`\n"
        f"Vendre sur : *{opp['sell_exchange']}* à `{opp['sell_price']}`\n"
        f"Spread brut : `{opp['gross_spread_pct']}%`\n"
        f"Spread net (frais déduits) : `{opp['net_spread_pct']}%`"
    )
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        logger.error(f"Erreur envoi Telegram: {e}")


async def send_status_message(text: str):
    """Envoie un message de statut générique (démarrage, erreurs, etc.)."""
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"Erreur envoi Telegram: {e}")
