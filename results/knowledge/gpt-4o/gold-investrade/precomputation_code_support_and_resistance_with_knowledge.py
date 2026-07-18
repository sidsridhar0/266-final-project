import pandas as pd
import argparse
from datetime import datetime, timedelta

def calculate_levels(data, end_date, product_name):
    # Convert dates to datetime
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Filter for the last 60 days and specified product
    start_date = end_date - timedelta(days=60)
    recent_data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date) & (data['Product Name'] == product_name)]

    # Forward fill missing values
    recent_data = recent_data.ffill()

    # Identify support and resistance levels
    support_levels = recent_data['Low'].min()
    resistance_levels = recent_data['High'].max()
    
    # Current price
    current_price = recent_data[recent_data['Date'] == end_date]['Close'].iloc[-1]

    # Calculate proximity
    distance_to_support = abs(current_price - support_levels)
    distance_to_resistance = abs(current_price - resistance_levels)

    # Determine nearest level
    proximity_to_levels = min(distance_to_support, distance_to_resistance)

    # Print results
    print(f"METRIC:support_levels\tVALUE:{support_levels}\tUNIT:none\tTYPE:float")
    print(f"METRIC:resistance_levels\tVALUE:{resistance_levels}\tUNIT:none\tTYPE:float")
    print(f"METRIC:proximity_to_levels\tVALUE:{proximity_to_levels}\tUNIT:none\tTYPE:float")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    
    args = parser.parse_args()
    
    # Read in the data
    data = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    
    # Convert the date of interest to a datetime object
    end_date = datetime.strptime(args.date, "%Y-%m-%d")
    
    # Perform the calculations and print results
    calculate_levels(data, end_date, args.product_name)
