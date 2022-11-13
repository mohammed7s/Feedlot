import pandas as pd


## Inputs

token_1 = 'USDC'
token_2 = 'WETH'
token_1_initial = 1000000

fee_rate = 0.01



## Analysis / AMM Modeling

# CPMM model: (x + dx) * (y - (1+s)*dy) = k 

df = pd.read_csv('cow-3month-download.csv')

# Filter trades of Pair needed : WETH-USDC
df = df[['block_time', 'buy_token', 'sell_token', 'units_bought', 'units_sold', 'trade_value_usd']]
df = df[((df.buy_token == token_1) & (df.sell_token == token_2)) | ((df.sell_token == token_1) & (df.buy_token == token_2))]

# add column: price
price = df.units_bought / df.units_sold
df['price'] = price 

#inspect cleaned data ready for analysis
pd.DataFrame(df).to_csv('inspect_df.csv', index=False)


# initialize pool 
s = fee_rate 
initialization_price = df.iloc[0,6]
print("initilization price = ", initialization_price)
token_2_initial = token_1_initial / initialization_price
k = token_1_initial * token_2_initial 
print('k= ', k) 
print('x= ', token_1_initial)
print('y= ', token_2_initial) 
print('s= ', s)


# initialize variables for the for loop
trades = 0 
fees = 0
volume = 0 
token_1_reserve = token_1_initial
token_2_reserve = token_2_initial

# go over trade by trade and check if it would have been executed or not
for i in range(len(df)):

    # if token_1 is the "buy token"
    if df.iloc[i,1] == token_1:
        y = token_1_reserve
        x = token_2_reserve 
        dx = df.iloc[i,4]
        dy = df.iloc[i,3]
        k_new = (x + dx) * (y - (1+s)*dy)   
        if k_new > k:
            trades = trades + 1 
            volume = volume + df.iloc[i,5]
            token_1_reserve = y-(1+s)*dy 
            token_2_reserve = x+dx 
            fees = fees + (s * df.iloc[i,5]) 

    # if token_2 is the "buy token"
    if df.iloc[i,1] == token_2:
        y = token_2_reserve
        x = token_1_reserve 
        dx = df.iloc[i,4]
        dy = df.iloc[i,3]
        k_new = (x + dx) * (y - (1+s)*dy)    
        if k_new > k: 
            trades = trades + 1 
            volume = volume + df.iloc[i,5]
            token_2_reserve = y-(1+s)*dy 
            token_1_reserve = x+dx 
            fees = fees + (s * df.iloc[i,5])

# Analysis 

total_trades = len(df) 
print('total_trades= ', total_trades)
print('trades executed = ', trades)

trades_executed_percentage = trades / total_trades * 100 
print('of trades executed = ', trades_executed_percentage, '%') 

print('total usd volume traded = ', volume)
print('fees collected', fees)  


