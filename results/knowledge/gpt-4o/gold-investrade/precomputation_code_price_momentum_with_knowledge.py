import pandas as pd
import numpy as np
import argparse

def calculate_metrics(data_path, product_name, date):
    # Read data
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    
    # Ensure correct data types
    df["Date"] = pd.to_datetime(df["Date"])
    df["Open"] = df["Open"].astype(float)
    df["Close"] = df["Close"].astype(float)
    
    # Filter by product name
    df = df[df["Product Name"] == product_name].copy()

    # Forward fill missing values
    df = df.ffill()

    # Calculate day-to-day price change
    df["price_change"] = df["Close"] - df["Open"]

    # Calculate RSI
    window_length = 14  # look-back period of RSI
    close_delta = df["Close"].diff()
    
    # Make the positive gains (up) and negative gains (down) Series
    up = close_delta.clip(lower=0)
    down = -close_delta.clip(upper=0)

    # Calculate the EWMA
    ma_up = up.rolling(window=window_length, min_periods=1).mean()
    ma_down = down.rolling(window=window_length, min_periods=1).mean()

    # Calculate the RSI based on EWMA
    rs = ma_up / ma_down
    df["RSI"] = 100 - (100 / (1 + rs))

    # Filter by the given date of interest
    result_row = df[df["Date"] == pd.to_datetime(date)]
    
    # Print results in the required format
    if not result_row.empty:
        price_change_value = result_row["price_change"].iloc[0]
        rsi_value = result_row["RSI"].iloc[0]

        print(f"METRIC:price_change\tVALUE:{price_change_value:.4f}\tUNIT:points\tTYPE:{type(price_change_value).__name__}")
        print(f"METRIC:RSI\tVALUE:{rsi_value:.4f}\tUNIT:index\tTYPE:{type(rsi_value).__name__}")
    else:
        print("No data available for the provided date.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate momentum metrics for a given product and date.")
    parser.add_argument('--data_path', type=str, required=True, help="Path to the price data CSV file")
    parser.add_argument('--product_name', type=str, required=True, help="Name of the product to analyze")
    parser.add_argument('--date', type=str, required=True, help="Date of interest for the analysis")
    args = parser.parse_args()
    
    calculate_metrics(args.data_path, args.product_name, args.date)
