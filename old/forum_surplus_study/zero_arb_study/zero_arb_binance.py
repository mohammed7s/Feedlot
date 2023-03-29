from datastreams.datastream import Streamer

import os
import pandas as pd
import polars as pl
import time 
import requests 

# initiate logger for trades analyzed in the while loop since run 
trades_analyzed = set()
headers_written = False
matching_trades=0 

while(True):

	# instantiate Streamer class. Note that we need two separate streamer classes, otherwise the queries will be overwritten. 
	cow_ds = Streamer('https://api.thegraph.com/subgraphs/name/cowprotocol/cow')
	cow_ds2 = Streamer('https://api.thegraph.com/subgraphs/name/cowprotocol/cow')


	# Query Params
	current_timestamp = int(time.time())
	# we set a fixed query size number large enough to retrieve all trades within 15mins 
	query_size = 1000
	# add timestamp of 15min limit (15 min = 900 seconds)  
	limit_timestamp = current_timestamp - 900 
	print('current timestamp: ', current_timestamp)

	# Query the Trades subgraph 

	# query COW schema: trades
	trades_fp = cow_ds.queryDict.get('trades')

	# trades query path that gets token a -> token b trades
	trades_qp = trades_fp(
	    first=query_size,
	    orderBy='timestamp',
	    where = {
	    'timestamp_gt': limit_timestamp
	    }
	)

	# run query
	trades_df = cow_ds.runQuery(trades_qp)

	# check results 
	print(f'query returned {len(trades_df)} rows')

	if len(trades_df) != 0: 
		unique_tokens = trades_df['trades_buyToken_id'].unique()
		print('unique tokens ', unique_tokens)
		#print('data types ', trades_df.dtypes)
		print('trades shape: ', trades_df.shape)


		# Query the Tokens subgraph

		# Set query size large enough to retrieve all tokens in the graph
		query_size = 10000

		token_fp = cow_ds2.queryDict.get('tokens')

		# add parameters to the settlements_qp.
		token_qp = token_fp(
		    first=query_size,
		)
		# run query
		token_df = cow_ds2.runQuery(token_qp)

		# check results
		print('tokens shape: ', token_df.shape)
		#print('data types ', token_df.dtypes)


		# Merge the two results into 1 dataframe 

		merged_df = pd.merge(trades_df, token_df, left_on='trades_sellToken_id', right_on='tokens_address')
		print('merge sell tokens complete: ', merged_df.shape)

		merged_df2 = pd.merge(merged_df, token_df, left_on='trades_buyToken_id', right_on='tokens_address')
		print('merge buy tokens complete: ', merged_df2.shape)

		# Clean formatting
		merged_df2 = merged_df2.rename(columns={
		    "tokens_symbol_x": "sell_token_symbol",
		    "tokens_symbol_y":"buy_token_symbol",
		    "tokens_decimals_x": "sell_token_decimal", 
		    "tokens_decimals_y": "buy_token_decimal"})

		# filter out unnecessary columns
		complete_trades_df = merged_df2[[
		    'trades_id',
		    'trades_timestamp', 
		    'trades_gasPrice', 
		    'trades_feeAmount',                 
		    'trades_txHash',                    
		    'trades_settlement_id',   
		    'trades_sellAmount',
		    'sell_token_decimal',
		    'trades_buyAmount',   
		    'buy_token_decimal',
		    'trades_sellToken_id',              
		    'trades_buyToken_id',               
		    'trades_order_id',                  
		    'sell_token_symbol',
		    'buy_token_symbol'
		    ]]


		# Filter out addresses that do not have a symbol in the subgraph
		complete_trades_df = complete_trades_df[complete_trades_df['buy_token_symbol'] != '']
		complete_trades_df = complete_trades_df[complete_trades_df['sell_token_symbol'] != '']
		print('complete_trades_df shape ', complete_trades_df.shape)

		# calculate buy and sell amounts from the correct decimal 
		complete_trades_df['sell_amount'] = complete_trades_df.apply(lambda x: x['trades_sellAmount'] / (10**x['sell_token_decimal']), axis=1)
		complete_trades_df['buy_amount'] = complete_trades_df.apply(lambda x: x['trades_buyAmount'] / (10**x['buy_token_decimal']), axis=1)

		# Caclculate COW price 
		complete_trades_df['cow_price'] = complete_trades_df['sell_amount'] / complete_trades_df['buy_amount']
		print(complete_trades_df.shape)


		print('complete_trades_df dataframe complete') 


		# Query Binance 

		host = "https://data.binance.com"
		prefix = "/api/v3/ticker/price"
		r = requests.get(host+prefix)
		data = r.json()
		binance_pairs = pd.DataFrame(data).loc[:,'symbol']

		def get_price_at_qty(symbol, qty):
		    url_vwap = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit=200'
		    r_vwap = requests.get(url_vwap)
		    data_vwap = r_vwap.json()
		    print('len of bids', len(data_vwap['bids']))
		    if len(data_vwap['bids']) != len(data_vwap['asks']):
		        return 'value_error'
		    df_vwap = pd.DataFrame(data_vwap)
		    df_vwap['bids'] = df_vwap['bids'].apply(lambda x: [float(i) for i in x])
		    df_vwap['asks'] = df_vwap['asks'].apply(lambda x: [float(i) for i in x])
		    
		    def get_price(data, qty):
		        total_qty = 0
		        price = None
		        for row in data:
		            row_qty = row[1]
		            row_price = row[0]
		            if total_qty + row_qty > qty:
		                remaining_qty = qty - total_qty
		                price = row_price
		                total_qty += remaining_qty
		                break
		            else:
		                total_qty += row_qty
		        return price

		    bid_price = get_price(df_vwap['bids'].values, qty)
		    ask_price = get_price(df_vwap['asks'].values, qty)
		    
		    if bid_price is None or ask_price is None:
    			print("Unable to calculate deviation due to missing price data")
    			return 'value_error'

		    bid_deviation = 100 * (bid_price - df_vwap['bids'][0][0]) / df_vwap['bids'][0][0]
		    ask_deviation = 100 * (ask_price - df_vwap['asks'][0][0]) / df_vwap['asks'][0][0]
		    
		    return bid_price, ask_price, bid_deviation, ask_deviation


		def query_binance(symbol: str, timestamp: int , qty:float, is_buy:bool):

		    """Queries the binance api to retrieve the price of symbol at a timestamp.
		    Timestamp has to be within 1000seconds window ~ 16.66 mins"""

		    host = "https://data.binance.com"
		    prefix = "/api/v3/klines"
		    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
		    payload = {'symbol':f'{symbol}','interval':'1s', 'limit':'1000'}
		    r = requests.get(host+prefix,  params=payload, headers=headers)
		    if r.status_code != 200:
		        print('API call failed with status code:', r.status_code)
		        return 'api error'
		    data = r.json()
		    df = pd.DataFrame(data).filter(items=[0,4],axis=1)
		    df.columns = ['timestamp', 'price']
		    df1 = df.loc[df['timestamp'] == timestamp*1000, 'price']
		    if df1.empty:
		        print('empty dataframe- no matching timestamp')
		        return 'no matching timestamp'
		    price = float(df1.iloc[0])
		    print(f'price for {symbol} is {price}')
		    
		    # adjust price by vwap estimate 
		    print('qty', qty)
		    ob = get_price_at_qty(symbol,qty)
		    print('ob', ob)
		    if ob != 'value_error':
		        if is_buy:
		            price_adjust = ob[3]
		            price_final = (price_adjust / 100 + 1) * price 
		        else: 
		            price_adjust = ob[2]
		            price_final = (1- price_adjust / 100) * price 
		    else:
		        return 'value_error'
		    
		    
		    return price_final 

		# test the binance_pairs array available

		if 'PERPUSDT' in binance_pairs.values:
		    print('True')
		else: 
		    print('False')


		def row_binance(sellTokenSymbol: str, buyTokenSymbol: str, timestamp: int, sellTokenQty:float, buyTokenQty:float):

			"""function to be used on the cow trades dataframe. Takes values from sellTokenSymbol 
			and buyTokenSymbol and timestamp to check the binance price for that trade. 

			Defines market_price as the price of sell token / price of buy token  
			Gets price of sell token and price of buy token from binance seperately

			Checks if token is USDT or a token that exists in Binance. Otherwise returns False 
			and not able to retrieve a price for that trade"""

			sell_pair = f'{sellTokenSymbol}USDT'
			buy_pair = f'{buyTokenSymbol}USDT'
			print('sell_pair: ', sell_pair)
			print('buy_pair: ', buy_pair)
			# retrieve sell token price  

			if sell_pair == 'USDTUSDT':
				sell_token_price = 1 
		        
		        
			elif sell_pair == 'DAIUSDT':
				usdtdai = query_binance('USDTDAI', timestamp, sellTokenQty, False)
				print('usdtdai result', usdtdai)
				if usdtdai != 'value_error' and type(usdtdai)==float and usdtdai!= 0 :
					sell_token_price = 1 / usdtdai
				else:
					return 'value_error'        
		        
		    
			elif sell_pair == 'WETHUSDT':
				sell_token_price = query_binance('ETHUSDT', timestamp,sellTokenQty, False)
		        
			elif sell_pair == 'WBTCUSDT':
				sell_token_price = query_binance('BTCUSDT', timestamp, sellTokenQty, False)
		        
			elif sell_pair in binance_pairs.values:
				sell_token_price = query_binance(sell_pair, timestamp, sellTokenQty, False)
		        
			else: 
				return 'sell_unavailable' 

			# retrieve buy token price 
		    
			if buy_pair =='USDTUSDT':
				buy_token_price = 1 
		        
		        
			elif buy_pair == 'DAIUSDT':
				usdtdai = query_binance('USDTDAI', timestamp, buyTokenQty, True)
				if usdtdai != 'value_error' and float(usdtdai) == 0 and usdtdai!=0 :
					buy_token_price = 1 / usdtdai
				else:
					return 'value_error'
		    
			elif buy_pair == 'WETHUSDT':
				buy_token_price = query_binance('ETHUSDT', timestamp, buyTokenQty, True)
		        
			elif buy_pair == 'WBTCUSDT':
				buy_token_price = query_binance('BTCUSDT', timestamp, buyTokenQty, True)
		        
			elif buy_pair in binance_pairs.values:
				buy_token_price = query_binance(buy_pair, timestamp, buyTokenQty, True)
		        
			else:
				return 'buy_unavailable'

			# calculate trade pair price 
			if buy_token_price != 'value_error' and buy_token_price != 'no matching timestamp':
				if sell_token_price != 'value_error' and sell_token_price != 'no matching timestamp':
					market_price = buy_token_price / sell_token_price 
					print(f'{sellTokenSymbol}/{buyTokenSymbol} binance price:', market_price)
					return market_price
				else:
					return 'value_error'
			else: 
				return 'value_error'



		# Initiate columns to be written in loop 
		complete_trades_df['binance_price'] = 0.0
		complete_trades_df = complete_trades_df.reset_index(drop=True)
		print(complete_trades_df)


		# Loop through each row of the dataframe.
		for i, row in complete_trades_df.iterrows():
		    # Retrieve the trades_id, timestamp, sell token symbol, and buy token symbol from the row.
		    trade_id = row[0]
		    print('trade_id', trade_id)
		    timestamp = row[1]
		    sell_token_symbol = row[13]
		    buy_token_symbol = row[14]
		    sell_token_qty = row[15]
		    buy_token_qty = row[16]
		    timestamp_now = int(time.time())
		    
		    # Check first if timestamp is within 1000s of now to avoid panick. If it is old, then return 'old timestamp' 
		    if abs(timestamp - timestamp_now) < 1000: 
		        if trade_id in trades_analyzed:
		        	complete_trades_df.iloc[i, 18] = 'repeat' 
        			# Skip this trade since it has already been analyzed
        			continue
        		else:
		            # Use the pair_price_binance function to calculate the binance price and store it in the dataframe.
		            complete_trades_df.iloc[i, 18] = row_binance(sell_token_symbol, buy_token_symbol, timestamp, sell_token_qty, buy_token_qty)
		            trades_analyzed.add(trade_id)
 
		            
		    else:
		        complete_trades_df.iloc[i, 18] = 'Timeout'
		    
		print('loop complete')

		# Filter out trades that do not have a symbol in the subgraph
		complete_trades_df = complete_trades_df[complete_trades_df['binance_price'] != 'repeat']
		complete_trades_df = complete_trades_df[complete_trades_df['binance_price'] != 'timeout']
		complete_trades_df = complete_trades_df[complete_trades_df['binance_price'] != 'buy_unavailable']
		complete_trades_df = complete_trades_df[complete_trades_df['binance_price'] != 'sell_unavailable']
		complete_trades_df = complete_trades_df[complete_trades_df['binance_price'] != 'value_error']

		# Define a percentage difference function to get percentage difference between binance price and cow price 

		def percentage_diff(col1, col2):
		    """
		    A function that calculates the percentage difference between two columns.
		    """
		    return ((col2.sub(col1)).div(col1)).mul(100)


		# Create a new column in the dataframe that stores the percentage difference between the sell amount and the sell amount on Binance.
		complete_trades_df['percentage_diff'] = percentage_diff(
		    complete_trades_df['cow_price'], 
		    complete_trades_df['binance_price']
		)

		# Filter out rows that have a difference higher than 50% as its likely to be a different token alltogether
		# an example is LIT which is Litentry on Binance but Timeless on COW. Unfortunately binance api does not allow
		# one to validate by token address only by string symbol. Its not perfect way to do it but at least filters the obvious ones out
		complete_trades_df = complete_trades_df[abs(complete_trades_df['percentage_diff']) < 50]

		# Append CSV file with results 
		if headers_written == False:
			complete_trades_df.to_csv('cow_binance_price_data.csv', mode='a', header=True, index=False)
			headers_written = True
		else:
			complete_trades_df.to_csv('cow_binance_price_data.csv', mode='a', header=False, index=False)
			headers_written = True


		matching_trades = matching_trades + len(complete_trades_df)

		# macro data for this run
		print('total cow trades so far: ', len(trades_analyzed))
		print('total number of matching trades appended to data: ', matching_trades)


	else: 
		print('no trades in this time period')

	# time the loop to run after 14mins of end of previous run. Though if there was a way to actually time it in 15mins intervals
	# that would be more efficient
	time.sleep(840)