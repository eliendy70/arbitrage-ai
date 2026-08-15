"""
Configuration centrale du bot.
Toutes les valeurs sensibles viennent d'un fichier .env (jamais commité).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # ton chat_id perso pour recevoir les alertes

# --- Exchanges à surveiller ---
# Ajoute ou retire des exchanges ici. Les clés API sont optionnelles
# si tu fais seulement de la détection (sans exécution automatique).
EXCHANGES = {
    "binance": {
        "api_key": os.getenv("BINANCE_API_KEY", ""),
        "secret": os.getenv("BINANCE_SECRET", ""),
    },
    "kraken": {
        "api_key": os.getenv("KRAKEN_API_KEY", ""),
        "secret": os.getenv("KRAKEN_SECRET", ""),
    },
    "kucoin": {
        "api_key": os.getenv("KUCOIN_API_KEY", ""),
        "secret": os.getenv("KUCOIN_SECRET", ""),
        "password": os.getenv("KUCOIN_PASSPHRASE", ""),
    },
}

# --- Paires à surveiller ---
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# --- Paramètres d'arbitrage ---
MIN_SPREAD_PERCENT = 0.5     # seuil minimum pour considérer une opportunité (%)
TAKER_FEE_ESTIMATE = 0.1     # frais moyen par exchange (%), utilisé pour le calcul net
CHECK_INTERVAL_SECONDS = 10  # fréquence de scan

# --- Mode ---
# "detection" = alertes uniquement (recommandé pour commencer)
# "execution" = exécute réellement les ordres (nécessite tests approfondis)
MODE = os.getenv("BOT_MODE", "detection")
