from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client
import colored
from colored import Fore, Back, Style
import requests
import playsound 
import sys
from playsound import playsound

import json
import websockets
import asyncio
from datetime import datetime


import sys
import time

api_key = ""

api_secret = ""



print(f"""{Fore.green}

                       _          _           _   
  ___ _ __ _   _ _ __ | |_ ___   | |__   ___ | |_ 
 / __| '__| | | | '_ \| __/ _ \  | '_ \ / _ \| __|
| (__| |  | |_| | |_) | || (_) | | |_) | (_) | |_ 
 \___|_|   \__, | .__/ \__\___/  |_.__/ \___/ \__|
           |___/|_|                               
--------------------------------------------------
Sell Bot

""")



def get_account_balances():
 
 # Create a new client object to interact with the Binance API
 client = Client(api_key, api_secret)


 # Retrieve the balances of all coins in the user’s Binance account
 account_balances = client.get_account()['balances']

 # Get the current price of all tickers from the Binance API
 ticker_info = client.get_all_tickers()

 # Create a dictionary of tickers and their corresponding prices
 ticker_prices = {ticker['symbol']: float(ticker['price']) for ticker in ticker_info}

 # Calculate the USDT value of each coin in the user’s account
 coin_values = []
 for coin_balance in account_balances:
  # Get the coin symbol and the free and locked balance of each coin
  coin_symbol = coin_balance['asset']
  unlocked_balance = float(coin_balance['free'])
  locked_balance = float(coin_balance['locked'])

  # If the coin is USDT and the total balance is greater than 1, add it to the list of coins with their USDT values
  if coin_symbol == 'USDT' and unlocked_balance + locked_balance > 1:
   coin_values.append(('USDT', (unlocked_balance + locked_balance)))
  # Otherwise, check if the coin has a USDT trading pair or a BTC trading pair
  elif unlocked_balance + locked_balance > 0.0:
   # Check if the coin has a USDT trading pair
   if (any(coin_symbol + 'USDT' in i for i in ticker_prices)):
    # If it does, calculate its USDT value and add it to the list of coins with their USDT values
    ticker_symbol = coin_symbol + 'USDT'
    ticker_price = ticker_prices.get(ticker_symbol)
    coin_usdt_value = (unlocked_balance + locked_balance) * ticker_price
    if coin_usdt_value > 1:
     coin_values.append((coin_symbol, coin_usdt_value))
   # If the coin does not have a USDT trading pair, check if it has a BTC trading pair
   elif (any(coin_symbol + 'BTC' in i for i in ticker_prices)):
    # If it does, calculate its USDT value and add it to the list of coins with their USDT values
    ticker_symbol = coin_symbol + 'BTC'
    ticker_price = ticker_prices.get(ticker_symbol)
    coin_usdt_value = (unlocked_balance + locked_balance) * ticker_price * ticker_prices.get('BTCUSDT')
    if coin_usdt_value > 1:
     coin_values.append((coin_symbol, coin_usdt_value))

 # Sort the list of coins and their USDT values by USDT value in descending order
 coin_values.sort(key=lambda x: x[1], reverse=True)

 # Return the list of coins and their USDT values
 return coin_values

 

 
def main():
 
    # Call the get_accountbalance function to get the list of coins and their USDT values
    coins_usdt_value = get_account_balances()

    # Print the list of coins and their USDT values in descending order of USDT value
    for coin, usdt_value in coins_usdt_value:
        print(f"{Fore.white}{coin}: ${usdt_value:.2f}")

    # Calculate the grand total USDT value
    grand_usdt_total = sum(map(lambda coin_usdt_value: coin_usdt_value[1], coins_usdt_value))

    
    
    # Print the grand total USDT value
    print(f"{Fore.white}\nBalance Total: ${grand_usdt_total:.2f}")
    print("------------------------------------------------")

    if grand_usdt_total > 1:
        print("You have more than 1 dollar Go ahead and do it!!")
    print("------------------------------------------------")
    

    

    

async def run_websocket():



    client = Client(api_key, api_secret)
    trade_coin = input("What coin will you trade? Enter trade pair in all CAPS: ")
    coin_price = client.get_symbol_ticker(symbol=trade_coin)
    trade = float(input(f"{trade_coin} price is {coin_price} what is the price you want to sell {trade_coin} ? "))
    #quantity = int(input(f"How many coins do you want to buy? "))
    stream = trade_coin + "@kline_1m"
    print(stream)

    quantity = int(input(f"How many coins do you want to sell? "))



    trade_coin_l = str(trade_coin).lower()
    param = (f"{trade_coin_l}@kline_1m")
    print(param)

    url = (f"wss://fstream.binance.com/stream?streams={param}")

    print(url)

    Verdad = True
    
    async with websockets.connect(url, ping_timeout=None, max_size=10000000) as websocket:
        url = (f"wss://fstream.binance.com/stream?streams={param}")
        
        headers = {"method": "SUBSCRIBE", "params": [param], "id": 1}
        await websocket.send(json.dumps(headers))
        while Verdad == True:
            msg = await websocket.recv()
            raw_data = json.loads(msg)
            if 'result' in raw_data:
                continue
            data = raw_data['data']
            pair = data['s']
            candle = data['k']
            dt_format = '%Y-%m-%d %H:%M:%S:%f'
            event_time = datetime.fromtimestamp(data['E'] / 1000).strftime(dt_format)
            minute = datetime.fromtimestamp(candle['t'] / 1000).strftime('%H:%M')
            price_stub = "{:.2f}"
            col_width = 8


            open_price = f"{price_stub.format(float(candle['o']))}{' ' * (col_width - len(price_stub.format(float(candle['o']))))}"
            close_price = f"{price_stub.format(float(candle['c']))}{' ' * (col_width - len(price_stub.format(float(candle['c']))))}"
            high_price = f"{price_stub.format(float(candle['h']))}{' ' * (col_width - len(price_stub.format(float(candle['h']))))}"
            low_price = f"{price_stub.format(float(candle['l']))}{' ' * (col_width - len(price_stub.format(float(candle['l']))))}"
            volume = candle['v']
            print(f'{Fore.white}[{event_time}] {pair} - minute: {minute} | open: {open_price} | close: {close_price} | '
                  f'high: {high_price} | low: {low_price} | volume: {volume} | '
                  f'quantity of coins is: {quantity}')
            

            def sell_coin():
                sell_order = client.order_market_sell(
                symbol=trade_coin, 
                quoteOrderQty =quantity)
                playsound('cash_sound.wav')
                playsound('bell.wav')
                Verdad = False

                quit()
    

          

            def watch_coin():

 
                if  float(open_price) >= trade:
                    print(f" SELL SELL SELL your sell price is {trade} the {trade_coin} price is {Fore.green}{open_price}")
                    sell_coin()
                                #rgb(255,140,0) dark orange
                else: print(f" {Fore.rgb(255, 140, 0)}NOT READY your SELL price is {Fore.rgb(0, 128, 0)}{trade} {Fore.white}the {trade_coin} price is {Fore.red}{open_price}")

            watch_coin()

    trade_coin_data = run_websocket(f"{trade_coin}@kline_1m")

    while grand_usdt_total > 1:
      #ETHUSDT_price = client.get_symbol_ticker(symbol="ETHUSDT")
      #print(ETHUSDT_price) 
      #REQBTC_price = client.get_symbol_ticker(symbol='REQBTC')
      #print(REQBTC_price)  
      #EOSETH_price = client.get_symbol_ticker(symbol='EOSETH')
      #print(EOSETH_price)
     asyncio.run(run_websocket())



if __name__ == '__main__':
    main()

if __name__ == '__main__':
    asyncio.run(run_websocket())











    #trade_coin_data = (f"wss://fstream.binance.com/stream?streams={trade_coin}@kline_1m")

    
   
  

    # requesting data for ADAUSDT
   # coin_data = requests.get(trade_coin_data) 
   # coin_data = coin_data.json() 
   # coin_price = float(coin_data['price'])


    

   # def buy_coin():
   #     buy_order = client.order_market_buy(
   #     symbol=trade_coin, 
   #     quoteOrderQty =100)

   # def sell_coin():
   #     buy_order = client.order_market_sell(
   #     symbol=trade_coin, 
   #     quoteOrderQty =100)

    # def watch_coin():

         # requesting data for LTCUSDT
      #  coin_data = requests.get(trade_coin_data) 
      #  coin_data =  coin_data.json() 
      #  coin_price = float(coin_data['price']) 

      #  if  coin_price <= trade:
       #     print(f" BUY BUY BUY your buy price is {trade} the {trade_coin} price is {coin_price}")
       #     buy_coin()

       # else: print(f" NOT READY your buy price is {trade} the {trade_coin} price is {coin_price}")

   

    


    #coin_price = client.get_symbol_ticker(symbol=trade_coin)
    #print(coin_price) 

  


    #while grand_usdt_total > 1:
      #ETHUSDT_price = client.get_symbol_ticker(symbol="ETHUSDT")
      #print(ETHUSDT_price) 
      #REQBTC_price = client.get_symbol_ticker(symbol='REQBTC')
      #print(REQBTC_price)  
      #EOSETH_price = client.get_symbol_ticker(symbol='EOSETH')
      #print(EOSETH_price)
     #   watch_coin()



     
#main()
#asyncio.run(run_websocket())




#First get ETH price

#client = Client(api_key, api_secret)




#ETHUSDT_price = client.get_symbol_ticker(symbol="ETHUSDT")
#print(ETHUSDT_price) 
#REQBTC_price = client.get_symbol_ticker(symbol='REQBTC')
#print(REQBTC_price)  
#EOSETH_price = client.get_symbol_ticker(symbol='EOSETH')
#print(EOSETH_price)



#buy_order = client.order_market_buy(
#                 symbol='REQBTC', 
#                 quoteOrderQty =100
#            )
