import json
import re
from config import BYBIT_API_KEY, BYBIT_SECRET_KEY, COINS_BYBIT
from config import INTERVAL, OUTPUTSIZE, EMA_PERIODS
import requests
import pandas as pd

from data_fetcher import add_technical_indicators

# GET /v5/market/mark-price-kline
# Response Example
#{
#    "retCode": 0,
#    "retMsg": "OK",
#    "result": {
#        "symbol": "BTCUSDT",
#        "category": "linear",
#        "list": [
#            [
#            "1670608800000",
#            "17164.16",
#            "17164.16",
#            "17121.5",
#            "17131.64"
#            ]
#        ]
#    },
#    "retExtInfo": {},
#    "time": 1672026361839
#}
interval_map = {
    "1min": "1",
    "5min": "5",
    "15min": "15",
    "30min": "30",
    "1h": "60",
}

def get_bybit_coin_data(coins: list[str], interval: str = INTERVAL, outputsize: int = OUTPUTSIZE):
    """Get data from bybit"""
    json_data = []
    for coin in coins:
        url = f"https://api.bybit.com/v5/market/mark-price-kline?symbol={coin}&interval={interval_map[interval]}&limit={outputsize}"
        response = requests.get(url)
        data = response.json()
        if data['retMsg'] == 'OK':
            df = pd.DataFrame(data['result']['list'], columns=['datetime', 'open', 'high', 'low', 'close'])
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            
            # Sort data chronologically (oldest first) - CRITICAL for indicators
            df = df.sort_values('datetime').reset_index(drop=True)
            
            df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert price columns to float, handling comma decimal separators
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
            df = add_technical_indicators(df)
            max_period = max(EMA_PERIODS)  # 200
            if len(df) > max_period:
                df = df.iloc[max_period:].reset_index(drop=True)
                print(f"Trimmed data: removed first {max_period} points, keeping {len(df)} points with full indicators")
            data['values'] = df.to_dict('records')
            json_data.append(data)
        else:
            raise Exception(f"Error: {json_data[0]['retMsg']}")
    return json_data

def get_instrument_information(category: str, coin: str, baseCoin: str):
    """Get instrument information from bybit """
    url = f"https://api.bybit.com/v5/market/instruments-info?category={category}&symbol={coin}&baseCoin={baseCoin}"
    response = requests.get(url)
    data = response.json()
    qty_info = data['result']['list'][0]['lotSizeFilter']
    leverage_info = data['result']['list'][0]['leverageFilter']
    if data['retMsg'] == 'OK':
        return {"minOrderQty": qty_info['minOrderQty'], "maxOrderQty": qty_info['maxOrderQty'],"qtyStep": qty_info['qtyStep'], "minLeverage": leverage_info['minLeverage'], "maxLeverage": leverage_info['maxLeverage']}
    else:
        raise Exception(f"Error: {data['retMsg']}")


def get_account_information(coin: str, baseCoin: str):
    """
    get the account information from bybit
    """
    url = f"https://api.bybit.com/v5/account/wallet-balance?coin={coin}&baseCoin={baseCoin}"
    response = requests.get(url)
    data = response.json()
    return data

def risk_management_information(message: str, coin: str, baseCoin: str):
    """
    define the lot size based on risk in message
    calculate the stack based on minimum qty and qtystep    
    """
    percent_account_load = 0.01


def decode_message(message: str):
    """
    decode the message to json
    """
    json_match = re.search(r'\{.*\}', message, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        data = json.loads(json_str)
        return data
    else:
        raise Exception("No JSON found in message")

def send_order(message: str, coin: str, baseCoin: str):
    extracted_json = decode_message(message)
    category = "linear"
    instrument_information = get_instrument_information(category=category, coin=coin, baseCoin=baseCoin)
    risk_management_information = risk_management_information(message=extracted_json, coin=coin, baseCoin=baseCoin)
    # TODO plcae_trace()
    pass


if __name__ == "__main__":
    coins = COINS_BYBIT
    #data = get_bybit_coin_data(coins)
    instrument_information = get_instrument_information(category="linear", coin="BTCUSDT", baseCoin="USDC")
    print(instrument_information)