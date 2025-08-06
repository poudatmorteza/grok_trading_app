import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import PNG_PATH, EMA_PERIODS, AI_OUTPUT_MODE, SIGNAL_FORMAT
import re
from playwright.sync_api import sync_playwright
import tempfile
import os
from pandas._libs.tslibs.np_datetime import OutOfBoundsDatetime

def format_ai_output(analysis_text: str, symbol: str):
    """Format AI output based on config settings"""
    entry, tp1, tp2, tp3, sl, signal, probability = extract_trading_levels(analysis_text)
    
    if AI_OUTPUT_MODE == "signal":
        # Return only trading signals
        signal_text = f"📊 #{symbol} SIGNALS:\n"
        if signal:
            signal_text += f"📈 Signal: {signal}\n"
        if probability:
            signal_text += f"🎯 Probability: {probability}%\n"
        if entry and SIGNAL_FORMAT.get("entry", True):
            signal_text += f"🎯 Entry: {entry:.4f}\n"
        if sl and SIGNAL_FORMAT.get("stoploss", True):
            signal_text += f"🛑 SL: {sl:.4f}\n"
        if tp1 and SIGNAL_FORMAT.get("tp1", True):
            signal_text += f"🎯 TP1: {tp1:.4f}\n"
        if tp2 and SIGNAL_FORMAT.get("tp2", True):
            signal_text += f"🎯 TP2: {tp2:.4f}\n"
        if tp3 and SIGNAL_FORMAT.get("tp3", True):
            signal_text += f"🎯 TP3: {tp3:.4f}\n"
        return signal_text
    
    elif AI_OUTPUT_MODE == "detailed":
        # Return only detailed analysis
        return f"🤖 AI Analysis for #{symbol}:\n{analysis_text}"
    
    else:  # "both"
        # Return both signal and detailed analysis
        signal_text = f"📊 #{symbol} SIGNALS:\n"
        if signal:
            signal_text += f"📈 Signal: {signal}\n"
        if probability:
            signal_text += f"🎯 Probability: {probability}%\n"
        if entry and SIGNAL_FORMAT.get("entry", True):
            signal_text += f"🎯 Entry: {entry:.4f}\n"
        if sl and SIGNAL_FORMAT.get("stoploss", True):
            signal_text += f"🛑 SL: {sl:.4f}\n"
        if tp1 and SIGNAL_FORMAT.get("tp1", True):
            signal_text += f"🎯 TP1: {tp1:.4f}\n"
        if tp2 and SIGNAL_FORMAT.get("tp2", True):
            signal_text += f"🎯 TP2: {tp2:.4f}\n"
        if tp3 and SIGNAL_FORMAT.get("tp3", True):
            signal_text += f"🎯 TP3: {tp3:.4f}\n"
        
        return f"{signal_text}\n\n🤖 Detailed Analysis:\n{analysis_text}"

def extract_trading_levels(analysis_text: str):
    """Extract entry, TP, and SL levels from AI analysis text"""
    entry = None
    tp1 = None
    tp2 = None
    tp3 = None
    sl = None
    signal = None
    probability = None

    try:
        # Try to parse as JSON first
        import json
        # Find JSON object in the text
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            print("=== JSON PARSED SUCCESSFULLY ===")
            print(f"Signal: {data.get('signal')}")
            print(f"Entry: {data.get('entry')}")
            print(f"Stop Loss: {data.get('stop_loss')}")
            print(f"TP1: {data.get('tp1')}")
            print(f"TP2: {data.get('tp2')}")
            print(f"TP3: {data.get('tp3')}")
            print("=== END JSON PARSED ===")
            
            # Extract values from JSON
            signal = data.get('signal', '').upper()
            entry = data.get('entry')
            sl = data.get('stop_loss')
            tp1 = data.get('tp1')
            tp2 = data.get('tp2')
            tp3 = data.get('tp3')
            probability = data.get('probability')
            
            return entry, tp1, tp2, tp3, sl, signal, probability
            
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"JSON parsing failed: {e}")
        # Fallback to regex parsing for backward compatibility
        pass
    
    # Fallback to regex parsing if JSON fails
    print("=== FALLBACK TO REGEX PARSING ===")
    
    # Debug: Look for trading signal section specifically
    signal_section = re.search(r'### IMMEDIATE TRADING SIGNAL.*?(?=###|$)', analysis_text, re.DOTALL | re.IGNORECASE)
    if signal_section:
        print("=== TRADING SIGNAL SECTION ===")
        print(signal_section.group(0))
        print("=== END TRADING SIGNAL SECTION ===")
    
    # More robust regex patterns that handle various formats
    patterns = {
        'signal': [
            r'\*\*SIGNAL\*\*:\s*(BUY|SELL|HOLD)',
            r'SIGNAL:\s*(BUY|SELL|HOLD)',
            r'Signal:\s*(BUY|SELL|HOLD)'
        ],
        'entry': [
            r'\*\*ENTRY\*\*:\s*([\d,]+\.?\d*)',
            r'ENTRY:\s*([\d,]+\.?\d*)',
            r'Entry:\s*([\d,]+\.?\d*)',
            r'\*\*ENTRY\*\*:\s*\n\s*([\d,]+\.?\d*)',  # Handle newline format
            r'\*\*ENTRY\*\*:\s*\n\s*\n\s*([\d,]+\.?\d*)'  # Handle double newline format
        ],
        'tp1': [
            r'\*\*TP1\*\*:\s*([\d,]+\.?\d*)',
            r'TP1:\s*([\d,]+\.?\d*)',
            r'\*\*TP1\*\*:\s*\n\s*([\d,]+\.?\d*)',  # Handle newline format
            r'\*\*TP1\*\*:\s*\n\s*\n\s*([\d,]+\.?\d*)'  # Handle double newline format
        ],
        'tp2': [
            r'\*\*TP2\*\*:\s*([\d,]+\.?\d*)',
            r'TP2:\s*([\d,]+\.?\d*)',
            r'\*\*TP2\*\*:\s*\n\s*([\d,]+\.?\d*)',  # Handle newline format
            r'\*\*TP2\*\*:\s*\n\s*\n\s*([\d,]+\.?\d*)'  # Handle double newline format
        ],
        'tp3': [
            r'\*\*TP3\*\*:\s*([\d,]+\.?\d*)',
            r'TP3:\s*([\d,]+\.?\d*)',
            r'\*\*TP3\*\*:\s*\n\s*([\d,]+\.?\d*)',  # Handle newline format
            r'\*\*TP3\*\*:\s*\n\s*\n\s*([\d,]+\.?\d*)'  # Handle double newline format
        ],
        'sl': [
            r'\*\*STOP LOSS\*\*:\s*([\d,]+\.?\d*)',
            r'STOP LOSS:\s*([\d,]+\.?\d*)',
            r'Stop Loss:\s*([\d,]+\.?\d*)',
            r'SL:\s*([\d,]+\.?\d*)',
            r'\*\*STOP LOSS\*\*:\s*\n\s*([\d,]+\.?\d*)',  # Handle newline format
            r'\*\*STOP LOSS\*\*:\s*\n\s*\n\s*([\d,]+\.?\d*)'  # Handle double newline format
        ]
    }
    
    # Try each pattern for each field
    for field, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, analysis_text, re.IGNORECASE)
            if match:
                print(f"Found {field}: {match.group(1)}")
                if field == 'signal':
                    signal = match.group(1).upper()
                else:
                    try:
                        # Remove commas and convert to float
                        value_str = match.group(1).replace(',', '')
                        value = float(value_str)
                        if field == 'entry':
                            entry = value
                        elif field == 'tp1':
                            tp1 = value
                        elif field == 'tp2':
                            tp2 = value
                        elif field == 'tp3':
                            tp3 = value
                        elif field == 'sl':
                            sl = value
                    except ValueError:
                        print(f"Could not parse {field} value: {match.group(1)}")
                break  # Found a match, no need to try other patterns for this field
    
    return entry, tp1, tp2, tp3, sl, signal, probability

def generate_charts(data: dict, analysis_text: str = "", exchange: str = ""):
    symbol, df = extract_df(data, exchange)
    
    # Use only last 20 bars for chart display (ensure correct order)
    df = df.tail(20).reset_index(drop=True)
    
    # Debug: Check chart data order
    if len(df) > 0:
        print(f"=== CHART DATA ===")
        print(f"Chart data points: {len(df)}")
        print(f"First entry: {df['datetime'].iloc[0]}")
        print(f"Last entry: {df['datetime'].iloc[-1]}")
        print(f"Latest price: {df['close'].iloc[-1]}")
        print("=== END CHART DATA ===")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Extract trading levels from analysis
    entry, tp1, tp2, tp3, sl, signal, probability = extract_trading_levels(analysis_text)
    
    # Create unique chart ID to prevent duplication
    chart_id = f"{symbol}_{timestamp}"
    
    # Create subplots: main chart and RSI
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} - Price & EMAs', 'RSI'),
        row_heights=[0.7, 0.3]
    )
    
    # Convert datetime strings back to datetime objects for proper x-axis formatting
    df['datetime_obj'] = pd.to_datetime(df['datetime'])
    
    # Add candlestick chart to first subplot
    fig.add_trace(go.Candlestick(
        x=df['datetime_obj'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red',
        showlegend=True,
        legendgroup="price",
        uid="price_candles"
    ), row=1, col=1)
    
    # Add EMAs to the first subplot
    ema_colors = ['blue', 'orange', 'red', 'green', 'purple']  # Colors for different EMAs
    for i, period in enumerate(EMA_PERIODS):
        ema_col = f'ema_{period}'
        if ema_col in df.columns:
            # Only plot EMA data where it's not NaN
            ema_data = df[df[ema_col].notna()]
            if len(ema_data) > 0:
                color = ema_colors[i % len(ema_colors)]
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(ema_data['datetime']), 
                    y=ema_data[ema_col], 
                    name=f'EMA {period}', 
                    line=dict(color=color, width=1), 
                    uid=f"ema_{period}"
                ), row=1, col=1)
    
    # Add trading levels as horizontal lines to first subplot
    if entry:
        fig.add_hline(y=entry, line_dash="solid", line_color="yellow", line_width=2, 
                     annotation_text=f"Entry: {entry:.2f}", row=1, col=1)
    if tp1:
        fig.add_hline(y=tp1, line_dash="dash", line_color="green", line_width=2,
                     annotation_text=f"TP1: {tp1:.2f}", row=1, col=1)
    if tp2:
        fig.add_hline(y=tp2, line_dash="dash", line_color="lime", line_width=2,
                     annotation_text=f"TP2: {tp2:.2f}", row=1, col=1)
    if tp3:
        fig.add_hline(y=tp3, line_dash="dash", line_color="lightgreen", line_width=2,
                     annotation_text=f"TP3: {tp3:.2f}", row=1, col=1)
    if sl:
        fig.add_hline(y=sl, line_dash="dash", line_color="red", line_width=2,
                     annotation_text=f"SL: {sl:.2f}", row=1, col=1)
    
    # Add RSI to second subplot
    if 'rsi' in df.columns:
        # Only plot RSI data where it's not NaN
        rsi_data = df[df['rsi'].notna()]
        if len(rsi_data) > 0:
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(rsi_data['datetime']), 
                y=rsi_data['rsi'], 
                name='RSI', 
                line=dict(color='purple'), 
                showlegend=True, 
                legendgroup="rsi", 
                uid="rsi_line"
            ), row=2, col=1)
        
        # Add overbought/oversold lines for RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="Overbought (70)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                     annotation_text="Oversold (30)", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'#{symbol} - Technical Analysis',
        template='plotly_dark',
        height=600,
        showlegend=True,
        uirevision=chart_id,  # Prevents chart duplication
        xaxis=dict(
            rangeslider=dict(visible=False),  # Remove zoom bar
            type='date',
            tickformat='%H:%M\n%m/%d',
            tickmode='auto',
            nticks=10
        )
    )
    
    # Update y-axis labels for subplots
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    
    # Try to save as PNG image for Telegram using Playwright
    try:
        png_path = f"{PNG_PATH}/{symbol.replace('/', '')}_{timestamp}.png"
        
        # Check for duplicate traces and subplot assignments
        trace_names = [trace.name for trace in fig.data]
        unique_traces = len(set(trace_names))
        print(f"Generating chart for {symbol} with {len(fig.data)} traces ({unique_traces} unique)")
        
        # Debug subplot assignments
        for i, trace in enumerate(fig.data):
            print(f"Trace {i}: {trace.name} -> row={getattr(trace, 'xaxis', 'N/A')}")
        
        # Save HTML temporarily
        temp_html = f"/tmp/chart_{timestamp}.html"
        fig.write_html(temp_html)
        
        # Convert HTML to PNG using Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file://{temp_html}")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=png_path, full_page=True)
            browser.close()
        
        # Clean up temp file
        os.remove(temp_html)
        print(f"Saved PNG: {png_path}")
        return png_path
    except Exception as e:
        print(f"PNG generation failed: {e}")
        # Fallback to HTML and text summary
        html_path = f"{PNG_PATH}/{symbol.replace('/', '')}_{timestamp}.html"
        fig.write_html(html_path)
        print(f"Saved HTML: {html_path}")
        
        # Create a text summary of the chart data with indicators
        latest_price = df['close'].iloc[-1]
        price_change = df['close'].iloc[-1] - df['open'].iloc[-1]
        price_change_pct = (price_change / df['open'].iloc[-1]) * 100
        high = df['high'].max()
        low = df['low'].min()
        
        # Add technical indicator summary
        rsi_text = ""
        ema_text = ""
        
        if 'rsi' in df.columns:
            current_rsi = df['rsi'].iloc[-1]
            rsi_status = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
            rsi_text = f"RSI: {current_rsi:.1f} ({rsi_status})"
        
        # Get EMA trend using first two EMA periods from config
        if len(EMA_PERIODS) >= 2:
            ema1_col = f'ema_{EMA_PERIODS[0]}'
            ema2_col = f'ema_{EMA_PERIODS[1]}'
            if ema1_col in df.columns and ema2_col in df.columns:
                ema1_val = df[ema1_col].iloc[-1]
                ema2_val = df[ema2_col].iloc[-1]
                ema_trend = "Bullish" if ema1_val > ema2_val else "Bearish"
                ema_text = f"EMA Trend: {ema_trend} ({EMA_PERIODS[0]}: {ema1_val:.2f}, {EMA_PERIODS[1]}: {ema2_val:.2f})"
        
        # Add trading levels to summary
        levels_text = ""
        if entry or tp1 or tp2 or tp3 or sl:
            levels_text = f"""
🎯 Trading Levels:
Entry: {entry:.2f if entry else 'N/A'}
TP1: {tp1:.2f if tp1 else 'N/A'}
TP2: {tp2:.2f if tp2 else 'N/A'}
TP3: {tp3:.2f if tp3 else 'N/A'}
SL: {sl:.2f if sl else 'N/A'}"""
        
        summary = f"""
📊 #{symbol} Technical Analysis:
💰 Current Price: {latest_price:.4f}
📈 Change: {price_change:+.4f} ({price_change_pct:+.2f}%)
📊 High: {high:.4f}
📉 Low: {low:.4f}
{rsi_text}
{ema_text}{levels_text}
⏰ Timeframe: Last 5 minutes
        """
        
        return summary

# Convert each symbol into a DataFrame
def extract_df(entry, exchange: str = ""):
    if exchange == "bybit":
        df = pd.DataFrame(entry['values'], columns=['datetime', 'open', 'high', 'low', 'close'])
    else:
        df = pd.DataFrame(entry['values'], columns=['datetime', 'open', 'high', 'low', 'close'])
    # Handle datetime conversion - check if it's already a string or needs conversion
    if df['datetime'].dtype == 'object':
        # Try to parse as datetime, handling different formats
        try:
            # First try standard datetime parsing with explicit format
            df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
        except (OutOfBoundsDatetime, OverflowError, ValueError):
            # If that fails, try parsing as Unix timestamp (milliseconds)
            try:
                df['datetime'] = pd.to_datetime(df['datetime'].astype(float), unit='ms')
            except (ValueError, OverflowError):
                # If that also fails, try seconds
                df['datetime'] = pd.to_datetime(df['datetime'].astype(float), unit='s')
    
    # Convert to string format if not already
    if df['datetime'].dtype != 'object':
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    
    # Only sort if not from Bybit (Bybit data is already sorted)
    if exchange != "bybit":
        df.sort_values('datetime', inplace=True)
        df.reset_index(drop=True, inplace=True)
    if exchange == "bybit":
        return entry['result']['symbol'], df
    else:
        return entry['meta']['symbol'], df