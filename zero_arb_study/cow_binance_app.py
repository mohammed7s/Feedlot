import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Define the function to read the data and return the latest 50 readings
def get_latest_data():
    df = pd.read_csv('cow_binance_price_data.csv')
    latest_data = df.tail(50)
    latest_data['timestamp'] = pd.to_datetime(latest_data['trades_timestamp'], unit='s')
    latest_data['timestamp'] = latest_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return latest_data

# Create the Streamlit app
def app():
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

    # Create bar plot
    fig, ax = plt.subplots()
    chart_data.plot(kind='bar', ax=ax)

    # Set plot labels
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Percentage Difference')

    # Show plot
    st.pyplot(fig)

if __name__ == '__main__':
    while True:
        app()
        time.sleep(900) # Refresh every 15 minutes


