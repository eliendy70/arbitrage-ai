"""
Point d'entrée du bot d'arbitrage.

Lance en parallèle :
1. La boucle de scan qui détecte les opportunités et alerte sur Telegram
2. Le bot Telegram interactif (/start, /stop, /status)
"""
import asyncio
import logging
from datetime import datetime

from config import SYMBOLS, CHECK_INTERVAL_SECONDS, MODE
from exchanges import init_exchanges
from arbitrage import find_opportunities
from execution import execute_arbitrage_trade
from notifier import send_opportunity_alert, send_trade_execution_alert, send_status_message
from telegram_commands import build_command_app, bot_state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def scan_loop():
    """Boucle infinie : scanne, détecte, alerte, patiente, recommence."""
    exchange_instances = init_exchanges()
    await send_status_message(
        f"🚀 Bot d'arbitrage démarré.\nMode : {MODE}\nPaires surveillées : {', '.join(SYMBOLS)}"
    )

    while True:
        if bot_state["running"]:
            try:
                opportunities = find_opportunities(exchange_instances, SYMBOLS)
                bot_state["last_scan"] = datetime.now().strftime("%H:%M:%S")

                for opp in opportunities:
                    bot_state["opportunities_found"] += 1
                    logger.info(f"Opportunité : {opp}")
                    await send_opportunity_alert(opp)

                    if MODE == "execution":
                        logger.info(f"Mode exécution activé. Lancement du trade d'arbitrage pour {opp['symbol']}...")
                        trade_res = execute_arbitrage_trade(opp, exchange_instances)
                        logger.info(f"Résultat trade : {trade_res}")
                        await send_trade_execution_alert(trade_res)

            except Exception as e:
                logger.error(f"Erreur dans la boucle de scan: {e}")
                await send_status_message(f"⚠️ Erreur : {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


async def main():
    command_app = build_command_app()

    async with command_app:
        await command_app.start()
        await command_app.updater.start_polling()
        await scan_loop()  # boucle principale (ne rend jamais la main)


if __name__ == "__main__":
    asyncio.run(main())
