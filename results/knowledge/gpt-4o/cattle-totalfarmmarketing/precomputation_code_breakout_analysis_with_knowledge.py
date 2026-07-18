import pandas as pd
import numpy as np
import argparse

def calculate_metrics(df, product_name, date_of_interest):
    # Ensure the correct data type
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', inplace=True)
    
    # Forward-fill missing data
    df.ffill(inplace=True)
    
    # Filter data for the specified product
    df = df[df['Product Name'] == product_name]
    
    # Calculate average volume for the last 20 days
    df['avg_volume_20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    
    # Identifying support and resistance levels
    df['support_level'] = df['Low'].rolling(window=20, min_periods=1).min()
    df['resistance_level'] = df['High'].rolling(window=20, min_periods=1).max()
    
    # Finding volume spike
    df['volume_spike'] = df['Volume'] > df['avg_volume_20']
    
    # Only consider the data up to the date of interest for analysis
    df = df[df['Date'] <= date_of_interest]

    # Get the latest entry to determine support, resistance, and volume spike
    last_entry = df.iloc[-1]

    # Printing results in required format
    metrics = [
        ("support_level", last_entry['support_level'], None, type(last_entry['support_level']).__name__),
        ("resistance_level", last_entry['resistance_level'], None, type(last_entry['resistance_level']).__name__),
        ("volume_spike", last_entry['volume_spike'], None, type(last_entry['volume_spike']).__name__)
    ]

    for metric, value, unit, dtype in metrics:
        print(f"METRIC:{metric}\tVALUE:{value}\tUNIT:{unit}\tTYPE:{dtype}")

def main():
    # Argument parser for command line arguments
    parser = argparse.ArgumentParser(description='Process data for breakout analysis.')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the data file.')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product.')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format.')

    args = parser.parse_args()
    
    # Load data from csv
    df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    
    # Call the function to calculate metrics
    calculate_metrics(df, args.product_name, args.date)
    
if __name__ == "__main__":
    main()
