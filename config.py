import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use environment variables
GROK_API_KEY = os.getenv("GROK_API_KEY", "your_grok_api_key_here")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "your_twelvedata_key_here")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "your_bybit_key_here")
BYBIT_SECRET_KEY = os.getenv("BYBIT_SECRET_KEY", "your_bybit_secret_here")
TG_API_KEY = os.getenv("TG_API_KEY", "your_telegram_key_here")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "your_chat_id_here")

# Iteractive Broker
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "your_demo_username")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "your_demo_password")

SYMBOLS = ["EUR/USD", "XAU/USD"]
COINS = ["BTC/USD", "ETH/USD", "SOL/USD"]
COINS_BYBIT = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
EXCHANGE = "Binance"
INTERVAL = "15min"
PNG_PATH = "/home/mortezapoudat/projects/ai_app/data/charts"
OUTPUTSIZE = 1000

# Technical Indicators Settings
EMA_PERIODS = [20, 50, 200]  # EMA periods to calculate
RSI_PERIOD = 14  # RSI calculation period
VOLATILITY_PERIOD = 20  # Rolling window for volatility calculation

# AI Output Settings
AI_OUTPUT_MODE = "both"  # Options: "signal", "detailed", "both"
SIGNAL_FORMAT = {
    "entry": True,
    "stoploss": True, 
    "tp1": True,
    "tp2": True,
    "tp3": True
}
