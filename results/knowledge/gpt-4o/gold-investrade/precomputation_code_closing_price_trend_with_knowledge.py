import pandas as pd
import numpy as np
import argparse
from datetime import datetime
from scipy.stats import linregress

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, required=True)
parser.add_argument('--product_name', type=str, required=True)
parser.add_argument('--date', type=str, required=True)
args = parser.parse_args()

# Load data
data = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])

# Ensure correct data types
data["Date"] = pd.to_datetime(data["Date"])
data["Open"] = pd.to_numeric(data["Open"], errors='coerce')
data["High"] = pd.to_numeric(data["High"], errors='coerce')
data["Low"] = pd.to_numeric(data["Low"], errors='coerce')
data["Close"] = pd.to_numeric(data["Close"], errors='coerce')
data["Volume"] = pd.to_numeric(data["Volume"], errors='coerce')

# Forward fill to handle missing values
data = data.ffill()

# Filter by product name
product_data = data[data["Product Name"] == args.product_name]

# Handle the date of interest
date_of_interest = pd.to_datetime(args.date)

# Calculate the closing price trend (slope of the linear regression line)
product_data.sort_values(by="Date", inplace=True)
latest_data = product_data[product_data["Date"] <= date_of_interest].tail(10)

slope, _, _, _, _ = linregress(range(len(latest_data)), latest_data['Close'])

# Calculate the 20-day Simple Moving Average (SMA)
product_data['SMA_20'] = product_data['Close'].rolling(window=20).mean()

# Calculate the 20-day Expotential Moving Average (EMA)
product_data['EMA_10'] = product_data['Close'].ewm(span=10, adjust=False).mean()

# Find the crossing point of SMA and EMA
sma_latest = product_data[product_data["Date"] == date_of_interest]['SMA_20'].values[0]
ema_latest = product_data[product_data["Date"] == date_of_interest]['EMA_10'].values[0]
closing_price_latest = product_data[product_data["Date"] == date_of_interest]['Close'].values[0]

# Print the results
print(f"METRIC:closing_price_trend\tVALUE:{slope}\tUNIT:\tTYPE:float")
print(f"METRIC:SMA-20\tVALUE:{sma_latest}\tUNIT:\tTYPE:float")
print(f"METRIC:EMA-10\tVALUE:{ema_latest}\tUNIT:\tTYPE:float")
print(f"METRIC:closing_price\tVALUE:{closing_price_latest}\tUNIT:\tTYPE:float")
