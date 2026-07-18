import pandas as pd
import numpy as np
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description='Analyze gold market volatility.')
parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV file containing market data')
parser.add_argument('--product_name', type=str, required=True, help='Product name to filter the data')
parser.add_argument('--date', type=str, required=True, help='Date for which to analyze volatility')
args = parser.parse_args()

# Read data
df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"], dtype={
    "Date": "str", 
    "Product Name": "str",
    "Symbol": "str",
    "Open": "float",
    "High": "float",
    "Low": "float",
    "Close": "float",
    "Volume": "float"
})

# Forward fill missing values
df = df.ffill()

# Filter data for the given product and sort by date
df = df[df['Product Name'] == args.product_name].sort_values(by='Date')

# Calculate daily range
df['daily_range'] = df['High'] - df['Low']

# Ensure 'Date' is the proper datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Calculate average daily range over the past 20 days
df['average_daily_range'] = df['daily_range'].rolling(window=20).mean()

# Calculate daily return and historical volatility
df['daily_return'] = df['Close'].pct_change()
df['historical_volatility'] = df['daily_return'].rolling(window=30).std()

# Filter data for the date of interest
current_data = df[df['Date'] == pd.to_datetime(args.date)]

# Output metrics
if not current_data.empty:
    current_daily_range = current_data.iloc[0]['daily_range']
    avg_daily_range = current_data.iloc[0]['average_daily_range']
    historical_volatility = current_data.iloc[0]['historical_volatility']
    
    print(f"METRIC:daily_range\tVALUE:{current_daily_range}\tUNIT:none\tTYPE:float")
    print(f"METRIC:average_daily_range\tVALUE:{avg_daily_range}\tUNIT:none\tTYPE:float")
    print(f"METRIC:historical_volatility\tVALUE:{historical_volatility}\tUNIT:none\tTYPE:float")
else:
    print("No data found for the given date and product name")
