# AI Trading Bot - Forex & Crypto Analysis

A comprehensive trading bot that combines AI analysis with technical indicators for forex and cryptocurrency trading.

## 🚀 Features

- **Multi-Exchange Support**: Bybit, TwelveData, Interactive Brokers
- **AI-Powered Analysis**: Groq AI integration for market analysis
- **Technical Indicators**: EMA, RSI, Volatility, and more
- **Automated Trading**: Signal generation and order placement
- **Real-time Monitoring**: Continuous market data tracking
- **Telegram Integration**: Instant notifications and alerts
- **Chart Generation**: Automated chart creation with Plotly

## 📦 Installation

### Quick Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai_app
```

2. **Install dependencies**
```bash
# Using the setup script
python setup.py

# Or manually
pip install -r requirements_minimal.txt
playwright install
```

3. **Configure API keys**
Edit `config.py` with your API keys:
```python
TWELVEDATA_API_KEY = "your_twelvedata_key"
GROK_API_KEY = "your_grok_key"
BYBIT_API_KEY = "your_bybit_key"
BYBIT_SECRET_KEY = "your_bybit_secret"
TG_API_KEY = "your_telegram_bot_key"
TG_CHAT_ID = "your_chat_id"
```

## 🔧 Configuration

### API Keys Required

- **TwelveData**: For forex and crypto market data
- **Groq**: For AI analysis
- **Bybit**: For crypto trading
- **Telegram**: For notifications
- **Interactive Brokers**: For forex trading (optional)

### Trading Settings

Edit `config.py` to customize:
- Trading symbols and pairs
- Technical indicator periods
- AI output format
- Risk management parameters

## 📊 Usage

### Basic Usage

```python
from main import run

# Run crypto analysis on Bybit
run(contxt="crypto", exchange="bybit")

# Run forex analysis
run(contxt="forex", exchange="twelvedata")
```

### Automated Trading

```python
# Start the automated bot
python main.py
```

The bot will:
1. Fetch market data
2. Apply technical indicators
3. Generate AI analysis
4. Create charts
5. Send signals via Telegram

### Manual Analysis

```python
from data_fetcher import get_bybit_coin_data
from grok_call import ask_grok
from charts import generate_charts

# Get market data
data = get_bybit_coin_data(['BTCUSDT'])

# Get AI analysis
analysis = ask_grok(data[0], 'crypto', 'bybit')

# Generate chart
chart_path = generate_charts(data[0], analysis, 'bybit')
```

## 🏦 Interactive Brokers Integration

For forex trading with IBKR:

```python
from ibkr_api import IBKRAPI
from config import DEMO_USERNAME, DEMO_PASSWORD

# Initialize IBKR client
ibkr = IBKRAPI(DEMO_USERNAME, DEMO_PASSWORD, demo=True)

# Authenticate
if ibkr.authenticate():
    # Get forex rates
    rates = ibkr.get_forex_rates(['EUR.USD', 'GBP.USD'])
    
    # Place order
    order = ibkr.place_order('EUR.USD', 'BUY', 1000, 'MKT')
```

## 📈 Technical Indicators

The bot calculates:
- **EMA**: Exponential Moving Averages (20, 50, 200 periods)
- **RSI**: Relative Strength Index
- **Volatility**: Price volatility measures
- **Support/Resistance**: Key price levels
- **Volume Analysis**: Trading volume patterns

## 🤖 AI Analysis

The AI provides:
- **Trend Analysis**: Bullish/Bearish/Sideways
- **Signal Generation**: BUY/SELL/HOLD recommendations
- **Risk Assessment**: Low/Medium/High risk levels
- **Entry/Exit Points**: Precise price levels
- **Probability Scores**: Confidence levels (0-100%)

## 📱 Telegram Integration

Receive instant notifications:
- Trading signals
- Market analysis
- Chart images
- Error alerts
- Bot status updates

## 🔒 Security

- All API communications use HTTPS
- OAuth 2.0 authentication for IBKR
- Secure credential management
- Demo mode for safe testing

## 📁 Project Structure

```
ai_app/
├── main.py                 # Main bot runner
├── config.py              # Configuration settings
├── data_fetcher.py        # Market data retrieval
├── charts.py              # Chart generation
├── grok_call.py           # AI analysis
├── bybit.py               # Bybit exchange integration
├── ibkr_api.py            # Interactive Brokers API
├── telegram.py            # Telegram notifications
├── requirements.txt       # Full dependencies
├── requirements_minimal.txt # Essential dependencies
├── setup.py              # Installation script
└── data/                 # Generated charts and data
```

## 🛠️ Development

### Adding New Exchanges

1. Create exchange module (e.g., `binance.py`)
2. Implement data fetching function
3. Add to main.py routing
4. Update configuration

### Customizing AI Analysis

Edit `grok_call.py` to modify:
- Analysis prompts
- Output format
- Technical indicators
- Risk parameters

### Adding New Indicators

1. Add calculation in `data_fetcher.py`
2. Update chart generation in `charts.py`
3. Include in AI analysis prompt

## 🚨 Error Handling

The bot includes comprehensive error handling:
- Network connectivity issues
- API rate limiting
- Invalid data responses
- Authentication failures
- Chart generation errors

## 📊 Performance Monitoring

Monitor bot performance:
- Signal accuracy
- Win/loss ratios
- Risk-adjusted returns
- API usage statistics

## 🔄 Updates and Maintenance

Regular updates include:
- New technical indicators
- Enhanced AI models
- Additional exchanges
- Security improvements
- Performance optimizations

## 📞 Support

For issues and questions:
- Check error logs
- Verify API configurations
- Test with demo accounts
- Review documentation

## 📄 License

This project is for educational and development purposes. Please review exchange terms of service and API usage policies.

## ⚠️ Disclaimer

This software is for educational purposes only. Trading involves risk and may result in financial loss. Always test with demo accounts and use proper risk management. 