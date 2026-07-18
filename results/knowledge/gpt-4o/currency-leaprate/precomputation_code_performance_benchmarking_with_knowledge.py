import pandas as pd
import argparse
from datetime import datetime, timedelta

# Set up argument parser
parser = argparse.ArgumentParser(description='Performance Benchmarking')
parser.add_argument('--data_path', type=str, required=True, help='Path to the data CSV file')
parser.add_argument('--product_name', type=str, required=True, help='Name of the product')
parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
args = parser.parse_args()

# Load data
data = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Filter data for the specified product
product_data = data[data['Product Name'] == args.product_name].copy()
product_data.sort_index(inplace=True)

# Handle missing/invalid values
product_data.dropna(inplace=True)

# Ensure appropriate data types
product_data['Open'] = product_data['Open'].astype(float)
product_data['High'] = product_data['High'].astype(float)
product_data['Low'] = product_data['Low'].astype(float)
product_data['Close'] = product_data['Close'].astype(float)
product_data['Volume'] = product_data['Volume'].astype(float)

# Get the date of interest
date_of_interest = pd.to_datetime(args.date)

# Calculate required metrics
# Daily Close Price
daily_close = product_data.loc[date_of_interest]['Close']

# Weekly Performance
last_week = date_of_interest - timedelta(weeks=1)
weekly_data = product_data.loc[last_week:date_of_interest]
weekly_close = weekly_data['Close'].iloc[-1]
weekly_performance = (daily_close - weekly_close) / weekly_close * 100

# Monthly Performance
last_month = date_of_interest - pd.DateOffset(months=1)
monthly_data = product_data.loc[last_month:date_of_interest]
monthly_close = monthly_data['Close'].iloc[-1]
monthly_performance = (daily_close - monthly_close) / monthly_close * 100

# Print results in the required format
print(f"METRIC:Daily Close Price\tVALUE:{daily_close}\tUNIT:\tTYPE:float")
print(f"METRIC:Weekly Performance\tVALUE:{weekly_performance:.4f}\tUNIT:percent\tTYPE:float")
print(f"METRIC:Monthly Performance\tVALUE:{monthly_performance:.4f}\tUNIT:percent\tTYPE:float")
