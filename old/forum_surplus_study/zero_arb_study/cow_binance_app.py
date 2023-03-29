import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings

# Ignore warnings from showing on the app 
warnings.filterwarnings("ignore")


def run_app():
	@st.cache(ttl=900) # set TTL (time to live) to 900 seconds (15minutes)

	# Define the function to read the data and return the latest 50 readings
	def get_latest_data():
		df = pd.read_csv('cow_binance_price_data.csv')
		latest_data = df.tail(50)
		latest_data['timestamp'] = pd.to_datetime(latest_data['trades_timestamp'], unit='s')
		latest_data['timestamp'] = latest_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
		return latest_data


	def get_macro_metric():
		df = pd.read_csv('cow_binance_price_data.csv')
		total = len(df)
		cow_better = len(df[df['percentage_diff'] > 0])
		cow_worse = len(df[df['percentage_diff'] < 0])
		return total, cow_worse, cow_better

	st.title('COW-Binance price compare')

	st.write("The code for this app and script to fetch data are available on: github.com/mohammed7s/feedlot/zero_arb_study\n\nThe price is defined as the (sell/buy) hence a higher number is a worse price.\nA positive price difference indicates COW price is better for the user by the percentage difference")
	st.write('This table shows the latest 50 readings:')

	# Call the function to get the latest data
	latest_data = get_latest_data()

	# Display the table with the latest data
	st.table(latest_data[['trades_timestamp', 'timestamp','trades_txHash', 'sell_token_symbol', 'buy_token_symbol','cow_price', 'binance_price', 'percentage_diff']])
	
	# Create the chart with the percentage difference
	chart_data = latest_data[['timestamp', 'percentage_diff']]   
	chart_data.set_index('timestamp', inplace=True)

	# Display the number of rows and counts of positive/negative percentage_diff
	
	total, cow_worse, cow_better = get_macro_metric()
	st.write('Total number of rows:', total)
	st.write('Number of rows with positive percentage_diff:', cow_better)
	st.write('Number of rows with negative percentage_diff:', cow_worse)




	# Create a button to download the data
	st.download_button(
		label='Download data',
		data=pd.read_csv('cow_binance_price_data.csv').to_csv(index=False),
		file_name='cow_binance_price_data.csv',
		mime='text/csv'
	)

	# Create bar plot
	fig, ax = plt.subplots()
	chart_data.plot(kind='bar', ax=ax)	
	# Set plot labels
	ax.set_xticklabels([])
	ax.set_xlabel('Timestamp')
	ax.set_ylabel('Percentage Difference')
	# Show plot
	st.pyplot(fig)





if __name__ == '__main__':
    run_app()