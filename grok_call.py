import json
from config import GROK_API_KEY
from groq import Groq
from telegram import send_message
from config import EMA_PERIODS, RSI_PERIOD

def make_prompt(data: dict, contxt: str, exchange: str):
    # Extract only the latest data points for current market analysis
    simplified_data = {}
    if exchange == "bybit":
        symbol = data['result']['symbol']
        values = data['values']  # Use processed data with indicators and proper sorting
    else:
        symbol = data['meta']['symbol']
        values = data['values']
    if len(values) > 0:
        # Send the most recent data points for current market analysis (limit to avoid context overflow)
        recent_values = values[-100:]  # Last 100 data points for current market conditions
        
        # Convert timestamps to strings for JSON serialization
        for item in recent_values:
            if 'datetime' in item:
                item['datetime'] = str(item['datetime'])
        
        simplified_data = {
            'symbol': symbol,
            'current_market_data': recent_values
        }

    
    return f"""You are Gork, an expert {contxt} trading analyst. Analyze CURRENT market conditions.

CURRENT MARKET DATA:
{json.dumps(simplified_data, indent=2)}

ANALYZE:
1. Current price action and indicators
2. EMA positions and crossovers
3. RSI levels and opportunities
4. Support/resistance levels
5. Volatility and momentum

OUTPUT FORMAT - RESPOND IN JSON:
{{
  "trend": "Bullish/Bearish/Sideways",
  "ema_status": "Current EMA positions",
  "rsi": "Current RSI value and interpretation",
  "volume": "Current volume analysis",
  "support": "Current support levels",
  "resistance": "Current resistance levels",
  "volatility": "Current volatility assessment",
  "signal": "BUY/SELL/HOLD",
  "probability": 85,
  "reason": "Technical reasoning",
  "entry": 157.16,
  "stop_loss": 156.50,
  "tp1": 158.51,
  "tp2": 159.00,
  "tp3": 160.00,
  "risk_level": "Low/Medium/High",
  "position_size": "Recommended % of capital",
  "timeframe": "Next 10-15 minutes"
}}

IMPORTANT: 
- Focus on CURRENT market conditions
- Use LATEST price values for entry, stop_loss, tp1, tp2, tp3
- Respond ONLY with valid JSON format
- Use actual price scale (e.g., BTC ~113,894, not 113.894)

TRADING LOGIC:
- BUY: SL below entry, TPs above entry
- SELL: SL above entry, TPs below entry

PROBABILITY:
- Assess confidence (0-100%)
- 80%+ for strong signals with multiple confirmations
- 50-70% for weaker signals
- Consider technical alignment, market conditions, volatility

Provide concise analysis for immediate trading decisions."""

AI_AGENT = "llama-3.3-70b-versatile"  # Best model for complex reasoning and detailed analysis
def ask_grok(data: dict, contxt: str, exchange: str):
    groq = Groq(api_key=GROK_API_KEY)
    prompt = make_prompt(data, contxt, exchange)
    #send_message(f"asking grok for {contxt} data:\n")
    #send_message(f"Prompt: {prompt}")
    response = groq.chat.completions.create(
        model=AI_AGENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
        stream=False
    )
    return response.choices[0].message.content