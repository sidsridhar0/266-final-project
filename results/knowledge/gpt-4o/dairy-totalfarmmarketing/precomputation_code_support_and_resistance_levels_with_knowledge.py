import pandas as pd
import numpy as np
import argparse

def calculate_support_resistance_levels(df, lookback_days=60):
    # Filter the data only for the last 60 days
    df = df.tail(lookback_days)
    
    # Calculate support and resistance levels
    support_level = df['Low'].mode().iloc[0] if not df['Low'].mode().empty else np.nan
    resistance_level = df['High'].mode().iloc[0] if not df['High'].mode().empty else np.nan
    
    return support_level, resistance_level

def main(data_path, product_name, date_of_interest):
    # Read the data
    df = pd.read_csv(data_path, parse_dates=['Date'], dtype={
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

    # Filter data for the given product
    df_product = df[df["Product Name"] == product_name]

    # Identify support and resistance levels
    support, resistance = calculate_support_resistance_levels(df_product)

    # Print results
    print("METRIC:Support Level\tVALUE:{}\tUNIT:price\tTYPE:float".format(support))
    print("METRIC:Resistance Level\tVALUE:{}\tUNIT:price\tTYPE:float".format(resistance))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Support and Resistance Level Calculator')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product to analyze')
    parser.add_argument('--date', type=str, required=True, help='Date of interest for analysis')

    args = parser.parse_args()
    main(args.data_path, args.product_name, args.date)
