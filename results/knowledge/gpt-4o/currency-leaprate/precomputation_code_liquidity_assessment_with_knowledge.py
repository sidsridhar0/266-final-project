import pandas as pd
import argparse
import numpy as np

# Setup argument parser
parser = argparse.ArgumentParser(description='Liquidity assessment calculations.')
parser.add_argument('--data_path', type=str, required=True, help='Path to the data file.')
parser.add_argument('--product_name', type=str, required=True, help='Name of the product.')
parser.add_argument('--date', type=str, required=True, help='Date of interest.')
args = parser.parse_args()

# Read data into DataFrame and specify correct dtypes
data = pd.read_csv(args.data_path, dtype={
    "Date": "str", 
    "Product Name": "str", 
    "Symbol": "str", 
    "Open": "float", 
    "High": "float", 
    "Low": "float", 
    "Close": "float", 
    "Volume": "float"
})

# Convert 'Date' to datetime and filter for the specific product
data['Date'] = pd.to_datetime(data['Date'])
data = data[data['Product Name'] == args.product_name].sort_values('Date')

# Handle missing or invalid data by dropping rows with NaN values
data = data.dropna()

# Calculate the required metrics
# 1. Average Daily Volume
data['Average Daily Volume'] = data['Volume'].rolling(window=14, min_periods=1).mean()

# 2. Average True Range (ATR)
data['High-Low'] = data['High'] - data['Low']
data['High-PrevClose'] = abs(data['High'] - data['Close'].shift(1))
data['Low-PrevClose'] = abs(data['Low'] - data['Close'].shift(1))
data['True Range'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
data['ATR'] = data['True Range'].rolling(window=14, min_periods=1).mean()

# 3. Volume to Price Volatility Ratio
data['Volume to Price Volatility Ratio'] = data['Average Daily Volume'] / data['ATR']

# Select data for the specified date
results_date = pd.to_datetime(args.date)
results = data[data['Date'] == results_date]

# Print results in the required format
for _, row in results.iterrows():
    print(f"METRIC:Average Daily Volume\tVALUE:{row['Average Daily Volume']}\tUNIT:shares\tTYPE:float")
    print(f"METRIC:Volume to Price Volatility Ratio\tVALUE:{row['Volume to Price Volatility Ratio']}\tUNIT:ratio\tTYPE:float")
