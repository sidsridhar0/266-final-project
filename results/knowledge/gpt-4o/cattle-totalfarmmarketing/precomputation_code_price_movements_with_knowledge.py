import pandas as pd
import argparse
import numpy as np

def calculate_volatility(data_path, product_name, date_of_interest):
    # Read data into pandas DataFrame
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Open", "High", "Low", "Close", "Volume"])
    
    # Filter by the product name
    df = df[df["Product Name"] == product_name]
    
    # Convert data types
    df['Date'] = pd.to_datetime(df['Date'])
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    
    # Sort by date to ensure proper lookback calculations
    df = df.sort_values('Date')
    
    # Drop rows with missing values
    df = df.dropna()
    
    # Calculate intraday range
    df['intraday_range'] = df['High'] - df['Low']
    
    # Calculate average intraday range over the past 30 days
    df['average_intraday_range'] = df['intraday_range'].rolling(window=30, min_periods=1).mean()
    
    # Calculate percentage volatility
    df['percentage_volatility'] = (df['intraday_range'] / df['Close']) * 100
    
    # Filter the data for the date of interest only after calculations
    date_interest_dt = pd.to_datetime(date_of_interest)
    current_record = df[df['Date'] == date_interest_dt]
    
    if not current_record.empty:
        current_intraday_range = current_record['intraday_range'].iloc[0]
        current_percentage_volatility = current_record['percentage_volatility'].iloc[0]
        average_intraday_range = current_record['average_intraday_range'].iloc[0]
        
        # Print results
        print(f"METRIC:intraday_range\tVALUE:{current_intraday_range}\tUNIT:none\tTYPE:float")
        print(f"METRIC:average_intraday_range\tVALUE:{average_intraday_range}\tUNIT:none\tTYPE:float")
        print(f"METRIC:percentage_volatility\tVALUE:{current_percentage_volatility}\tUNIT:percent\tTYPE:float")
    else:
        print("No data available for the specified date of interest.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process cattle market data.')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the data file')
    parser.add_argument('--product_name', type=str, required=True, help='Product name to filter data')
    parser.add_argument('--date', type=str, required=True, help='Date of interest for calculations')
    args = parser.parse_args()
    
    calculate_volatility(args.data_path, args.product_name, args.date)
