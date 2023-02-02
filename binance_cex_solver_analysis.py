# CEX Solver price analysis 

import pandas as pd
import requests

def query_binance(symbol, timestamp):
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
	host = "https://data.binance.com"
	prefix = "/api/v3/ticker/price"
	r = requests.get(host+prefix)
	data = r.json()
	df_pairs = pd.DataFrame(data).loc[:,'symbol']
	binance_pairs.to_csv('binance_pairs.csv', index=False)


def pair_price_binance(sellTokenSymbol, buyTokenSymbol, timestamp):
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



pair_price_binance('ETH','USDT', 1675346048)



