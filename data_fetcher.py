import requests
import pandas as pd
import pandas_ta as ta
import numpy as np
from config import TWELVEDATA_API_KEY, EMA_PERIODS, RSI_PERIOD, VOLATILITY_PERIOD

def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """Calculate EMA using pandas-ta"""
    return ta.ema(data, length=period)

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI using pandas-ta"""
    return ta.rsi(data, length=period)

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add EMA, RSI, and other technical indicators to the dataframe using pandas-ta"""
    # Calculate EMAs dynamically from config
    for period in EMA_PERIODS:
        df[f'ema_{period}'] = calculate_ema(df['close'], period)
    
    # Calculate RSI using pandas-ta
    df['rsi'] = calculate_rsi(df['close'], RSI_PERIOD)
    
    # Debug: Print RSI values for last few data points
    if len(df) > 0:
        last_rsi_values = df['rsi'].tail(5).values
        print(f"Last 5 RSI values: {last_rsi_values}")
        print(f"RSI range: {df['rsi'].min():.2f} - {df['rsi'].max():.2f}")
    
    # Calculate price changes
    df['price_change'] = df['close'].diff()
    df['price_change_pct'] = df['close'].pct_change() * 100
    
    # Calculate volatility using pandas-ta
    df['volatility'] = ta.stdev(df['close'], length=VOLATILITY_PERIOD)
    
    # Add additional useful indicators
    df['sma_20'] = ta.sma(df['close'], length=20)  # Simple Moving Average
    
    return df

def get_symbol_data(symbols: list[str], outputsize: int = 1000):
    """Get forex data with more historical data points"""
    json_data = []
    for symbol in symbols:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize={outputsize}&apikey={TWELVEDATA_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        # Add technical indicators if data is valid
        if 'values' in data and data['status'] == 'ok':
            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            # Sort data chronologically (oldest first) - CRITICAL for indicators
            df = df.sort_values('datetime').reset_index(drop=True)
            
            # Convert price columns to float
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
            
            df = add_technical_indicators(df)
            
            # Remove the first 200 data points where indicators are not fully available
            # This ensures all EMAs (20, 50, 200) and RSI are available
            max_period = max(EMA_PERIODS)  # 200
            if len(df) > max_period:
                df = df.iloc[max_period:].reset_index(drop=True)
                print(f"Trimmed data: removed first {max_period} points, keeping {len(df)} points with full indicators")
            
            # Convert datetime to string format for JSON compatibility
            df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert back to dict format with indicators
            data['values'] = df.to_dict('records')
        
        json_data.append(data)
    return json_data

def get_coin_data(coins: list[str], exchange: str, outputsize: int = 1000):
    """Get crypto data with more historical data points"""
    json_data = []
    for coin in coins:
        url = f"https://api.twelvedata.com/time_series?symbol={coin}&interval=1min&exchange={exchange}&outputsize={outputsize}&apikey={TWELVEDATA_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        # Add technical indicators if data is valid
        if 'values' in data and data['status'] == 'ok':
            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            # Sort data chronologically (oldest first) - CRITICAL for indicators
            df = df.sort_values('datetime').reset_index(drop=True)
            
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
            df = add_technical_indicators(df)
            
            # Remove the first 200 data points where indicators are not fully available
            # This ensures all EMAs (20, 50, 200) and RSI are available
            max_period = max(EMA_PERIODS)  # 200
            if len(df) > max_period:
                df = df.iloc[max_period:].reset_index(drop=True)
                print(f"Trimmed data: removed first {max_period} points, keeping {len(df)} points with full indicators")
            
            # Convert datetime to string format for JSON compatibility
            df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert back to dict format with indicators
            data['values'] = df.to_dict('records')
        
        json_data.append(data)
    return json_data

