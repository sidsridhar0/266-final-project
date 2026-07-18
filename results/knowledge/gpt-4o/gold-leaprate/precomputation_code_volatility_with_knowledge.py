import pandas as pd
import numpy as np
import argparse

def calculate_volatility(df, date_of_interest, product_name):
    # Ensure the 'Date' column is a datetime object
    df['Date'] = pd.to_datetime(df['Date'])

    # Filter for the specified product name
    df = df[df['Product Name'] == product_name]

    # Sort values by 'Date'
    df = df.sort_values(by='Date')

    # Forward fill missing values
    df = df.ffill()

    # Calculate daily volatility
    df['daily_volatility'] = df['High'] - df['Low']

    # Filter by the date of interest
    df_of_interest = df[df['Date'] == date_of_interest]

    if not df_of_interest.empty:
        daily_volatility = df_of_interest['daily_volatility'].values[0]
        print(f"METRIC:daily_volatility\tVALUE:{daily_volatility}\tUNIT:currency\tTYPE:float")

    # Calculate percentage daily returns
    df['daily_return'] = df['Close'].pct_change()

    # Calculate historical volatility: standard deviation of daily returns over the past 30 days
    df['historical_volatility'] = df['daily_return'].rolling(window=30).std() * np.sqrt(252)  # Annualize volatility

    # Get the historical volatility for the date of interest
    df_of_interest = df[df['Date'] == date_of_interest]

    if not df_of_interest.empty:
        historical_volatility = df_of_interest['historical_volatility'].values[0]
        print(f"METRIC:historical_volatility\tVALUE:{historical_volatility}\tUNIT:none\tTYPE:float")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process volatility calculations.')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the data file')
    parser.add_argument('--product_name', type=str, required=True, help='Product name to filter data')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')

    args = parser.parse_args()

    # Read data from CSV
    df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])

    calculate_volatility(df, args.date, args.product_name)
