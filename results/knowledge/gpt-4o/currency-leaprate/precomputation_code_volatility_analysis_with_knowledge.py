import pandas as pd
import argparse

def calculate_metrics(df, product_name, date):
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Filter for the specific product
    df = df[df['Product Name'] == product_name]

    # Sort by date
    df = df.sort_values('Date')

    # Calculate Daily High-Low Range
    df['Daily High-Low Range'] = df['High'] - df['Low']

    # Calculate Average True Range (ATR) - 14-day average of the Daily High-Low Range
    df['ATR'] = df['Daily High-Low Range'].rolling(window=14, min_periods=1).mean()

    # Calculate Volume Change as percentage
    df['Volume Change'] = df['Volume'].pct_change() * 100
    
    # Handling missing values
    df.fillna(0, inplace=True)

    # Filter at the specific date
    df_date = df[df['Date'] == pd.to_datetime(date)]

    # Output the results on the specified date
    if not df_date.empty:
        metrics_to_output = [
            ('Daily High-Low Range', 'float', df_date['Daily High-Low Range'].iloc[0], None),
            ('Average True Range (ATR)', 'float', df_date['ATR'].iloc[0], None),
            ('Volume Change', 'percent', df_date['Volume Change'].iloc[0], 'float')
        ]
        
        for metric_name, unit, value, dtype in metrics_to_output:
            print(f"METRIC:{metric_name}\tVALUE:{value:.6f}\tUNIT:{unit}\tTYPE:{dtype}")
    else:
        print("No data available for the specified date and product.")

def main():
    parser = argparse.ArgumentParser(description='Calculate volatility-related metrics.')
    parser.add_argument('--data_path', type=str, help='Path to the CSV data file')
    parser.add_argument('--product_name', type=str, help='Name of the product to analyze')
    parser.add_argument('--date', type=str, help='Date of interest in format YYYY-MM-DD')
    args = parser.parse_args()

    # Read the CSV file
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

    calculate_metrics(df, args.product_name, args.date)

if __name__ == '__main__':
    main()
