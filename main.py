import os
import schedule
import time
from config import SYMBOLS, COINS, EXCHANGE, COINS_BYBIT
from data_fetcher import get_symbol_data, get_coin_data
from charts import generate_charts, format_ai_output
from grok_call import ask_grok
from telegram import send_image, send_message
from bybit import get_bybit_coin_data, send_order

def run(contxt="crypto", exchange="bybit"):
    #data = get_symbol_data(symbols=SYMBOLS)
    if contxt == "crypto":
        if exchange == "bybit":
            data = get_bybit_coin_data(coins=COINS_BYBIT)
        else:
            data = get_coin_data(coins=COINS, exchange=EXCHANGE)
    elif contxt == "forex":
        data = get_symbol_data(symbols=SYMBOLS)
    else:
        raise ValueError(f"Invalid context: {contxt}")
    #print(data)
    # Send data to ollama and get analysis
    for symbol in data:
        analysis = ask_grok(data=symbol, contxt=contxt, exchange=exchange)
        chart_result = generate_charts(symbol, analysis, exchange=exchange)
        
        # Format AI output based on config settings
        if exchange == "bybit":
            formatted_analysis = format_ai_output(analysis, symbol['result']['symbol'])
        else:
            formatted_analysis = format_ai_output(analysis, symbol['meta']['symbol'])
        
        # Check if we got a PNG path or text summary
        if chart_result.endswith('.png'):
            # Send PNG image and formatted analysis
            send_image(chart_result)
            send_message(formatted_analysis)
            
            #send_order(message=formatted_analysis, coin=symbol['result']['symbol'], baseCoin="USDC")
        else:
            # Send text summary and formatted analysis
            send_message(f"{chart_result}\n\n{formatted_analysis}")
    # TODO parse the answer
    # TODO send the prdictions to telegram



if __name__ == "__main__":
    contxt = "crypto"
    exchange = "bybit"
    bot_interval = 1
    schedule.every(bot_interval).minutes.do(run, contxt=contxt, exchange=exchange)

    send_message(f"Bot started in {contxt} mode in #{exchange} exchange")
    send_message(f"Running every {bot_interval} minutes...")

    while True:
        schedule.run_pending()
        time.sleep(1)
    