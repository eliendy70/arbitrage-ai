"""
Commandes Telegram interactives : /start, /stop, /status.
Permet de piloter le bot directement depuis Telegram.
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)

# État partagé simple (pour un bot mono-utilisateur ; passer à une DB si multi-user)
bot_state = {"running": True, "last_scan": None, "opportunities_found": 0}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_state["running"] = True
    await update.message.reply_text("✅ Surveillance d'arbitrage activée.")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_state["running"] = False
    await update.message.reply_text("⏸️ Surveillance mise en pause.")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = "actif" if bot_state["running"] else "en pause"
    await update.message.reply_text(
        f"État : {state}\n"
        f"Dernier scan : {bot_state['last_scan'] or 'aucun'}\n"
        f"Opportunités trouvées (session) : {bot_state['opportunities_found']}"
    )


def build_command_app() -> Application:
    """Construit l'application Telegram avec les handlers de commandes."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("status", status_command))
    return app
