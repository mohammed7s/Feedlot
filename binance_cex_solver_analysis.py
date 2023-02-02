# CEX Solver price analysis 

import pandas as pd
import requests

def query_binance(symbol, timestamp):

	"""Queries the binance api to retrieve the price of symbol at a timestamp.
	Timestamp has to be within 1000seconds window ~ 16.66 mins"""

	host = "https://data.binance.com"
	prefix = "/api/v3/klines"
	headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
	payload = {'symbol':f'{symbol}','interval':'1s', 'limit':'1000'}
	r = requests.get(host+prefix,  params=payload, headers=headers)
	data = r.json()
	df = pd.DataFrame(data).filter(items=[0,4],axis=1)
	df.columns = ['timestamp', 'price']
	price = float(df.loc[df['timestamp'] == timestamp*1000, 'price'].iloc[0])
	return price 


def get_binance_pairs():

	""" Used to get the list of symbols in binance. 
	The list is used as filter to check if the symbol exists in Binance or not" """

	host = "https://data.binance.com"
	prefix = "/api/v3/ticker/price"
	r = requests.get(host+prefix)
	data = r.json()
	df_pairs = pd.DataFrame(data).loc[:,'symbol']
	binance_pairs.to_csv('binance_pairs.csv', index=False)


def pair_price_binance(sellTokenSymbol, buyTokenSymbol, timestamp):

	"""function to be used on the cow trades dataframe. Takes values from sellTokenSymbol 
	and buyTokenSymbol and timestamp to check the binance price for that trade. 

	Defines market_price as the price of sell token / price of buy token  
	Gets price of sell token and price of buy token from binance seperately

	Checks if token is USDT or a token that exists in Binance. Otherwise returns False 
	and not able to retrieve a price for that trade"""

	df_binance_pairs_list = pd.read_csv('binance_pairs.csv').values
	sell_pair = f'{sellTokenSymbol}USDT'
	buy_pair = f'{buyTokenSymbol}USDT'

	# retrieve sell token price  

	if sell_pair == 'USDTUSDT':
		sell_token_price = 1 
	elif sell_pair in df_binance_pairs_list:
		sell_token_price = query_binance(sell_pair, timestamp)
	else: 
		return False 

	# retrieve buy token price 
	if buy_pair =='USDTUSDT':
		buy_token_price = 1 
	elif buy_pair in df_binance_pairs_list:
		buy_token_price = query_binance(buy_pair, timestamp)
	else:
		return False

	# calculate trade pair price 
	market_price = sell_token_price / buy_token_price 
	print(f'{sellTokenSymbol}/{buyTokenSymbol} binance price:', market_price)
	return market_price


#query_binance('ETHUSDT', 1675346048)



get_binance_pairs()

pair_price_binance('ETH','USDT', 1675346048)



