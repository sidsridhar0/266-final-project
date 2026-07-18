import pandas as pd
import numpy as np
import argparse
from datetime import datetime, timedelta

def load_data(data_path):
    data = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"], dtype={
        "Date": str,
        "Product Name": str,
        "Symbol": str,
        "Open": float,
        "High": float,
        "Low": float,
        "Close": float,
        "Volume": float
    })
    data["Date"] = pd.to_datetime(data["Date"], format='%Y-%m-%d', errors='coerce')
    return data.dropna()

def calculate_support_resistance(data, product_name, date):
    end_date = pd.to_datetime(date)
    start_date = end_date - timedelta(days=30)

    product_data = data[(data['Product Name'] == product_name) & (data['Date'] >= start_date) & (data['Date'] <= end_date)]

    # Calculating key support level (lowest price level with most bounces)
    support_level = product_data.groupby('Low').size().idxmax()
    
    # Calculating key resistance level (highest price level with most rejects)
    resistance_level = product_data.groupby('High').size().idxmax()

    return support_level, resistance_level

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()

    data = load_data(args.data_path)
    support_level, resistance_level = calculate_support_resistance(data, args.product_name, args.date)

    # Printing results
    print(f"METRIC: Key Support Level\tVALUE: {support_level}\tUNIT: price\tTYPE: float")
    print(f"METRIC: Key Resistance Level\tVALUE: {resistance_level}\tUNIT: price\tTYPE: float")

if __name__ == '__main__':
    main()
