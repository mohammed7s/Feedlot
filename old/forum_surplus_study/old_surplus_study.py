import pandas as pd


## Inputs

token_1 = 'USDC'
token_2 = 'WETH'
token_1_initial = 10000000


fee_rate = 0.02


## Analysis / AMM Modeling

# CPMM model: (x + dx) * (y - (1+s)*dy) = k 

df = pd.read_csv('cow-3month-download.csv')

# Filter trades of Pair needed : WETH-USDC
df = df[['block_time', 'buy_token', 'sell_token', 'units_bought', 'units_sold', 'trade_value_usd']]
df = df[((df.buy_token == token_1) & (df.sell_token == token_2)) | ((df.sell_token == token_1) & (df.buy_token == token_2))]



# add price column 
df['price'] = 0
for i in range(len(df)):
    if df.iloc[i,1] == token_1:
        df.iloc[i,6] = df.iloc[i,3] / df.iloc[i,4]

    if df.iloc[i,1] == token_2:
        df.iloc[i,6] = df.iloc[i,4] / df.iloc[i,3]

df['change%'] = df['price'].pct_change(-1)*100

#with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print('df', df.head(5))

# add columns: price/ difference / executed? 
df['surplus_k'] = 0
df['executed?'] = 0 
df['surplus_volume'] =0 



#inspect cleaned data ready for analysis
pd.DataFrame(df).to_csv('debug1.csv', index=False)


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
surplus = 0 
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
        k = y *x 
        k_new = (x + dx) * (y - (1+s)*dy)   
        if k_new > k:
            volume = volume + df.iloc[i,5]
            token_1_reserve = y-(1+s)*dy 
            token_2_reserve = x+dx 
            fees = fees + (s * df.iloc[i,5]) 
            trades = trades + 1 
            df.iloc[i,9] = 1 # trade executed signal 
            df.iloc[i,8] = k_new - k 



    # if token_2 is the "buy token"
    elif df.iloc[i,1] == token_2:
  `      y = token_2_reserve
        x = token_1_reserve 
        dx = df.iloc[i,4] 
        dy = df.iloc[i,3]
        k = y * x 
        k_new = (x + dx) * (y - (1+s)*dy)    
        if k_new > k: 
            volume = volume + df.iloc[i,5]
            token_2_reserve = y-(1+s)*dy 
            token_1_reserve = x+dx
            fees = fees + (s * df.iloc[i,5]) 
            trades = trades + 1 
            df.iloc[i,9] = 1 # trade executed signal 
            df.iloc[i,8] = k_new - k 




# Analysis 

total_trades = len(df) 
print('total_trades= ', total_trades)
print('trades executed = ', trades)
trades_executed_percentage = trades / total_trades * 100 
print('percentage of trades executed = ', trades_executed_percentage, '%') 
print('total usd volume traded = ', volume)
print('fees collected', fees)  

df.to_csv('debug2.csv')



# Fix the .loc and .iloc for price estimates
# Create volatility measure from previous pricing 
# import B2B block to block volatility measure.  