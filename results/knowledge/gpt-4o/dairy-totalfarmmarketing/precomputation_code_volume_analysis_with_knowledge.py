import pandas as pd
import argparse
from datetime import datetime

# Set up argument parser
parser = argparse.ArgumentParser(description='Market participation analysis')
parser.add_argument('--data_path', type=str, required=True, help='Path to CSV data file')
parser.add_argument('--product_name', type=str, required=True, help='Name of the product')
parser.add_argument('--date', type=str, required=True, help='Date of interest')

args = parser.parse_args()

# Read data
df = pd.read_csv(args.data_path)

# Ensure correct data types
df['Date'] = pd.to_datetime(df['Date'])
df = df.astype({
    'Product Name': 'str',
    'Symbol': 'str',
    'Open': 'float',
    'High': 'float',
    'Low': 'float',
    'Close': 'float',
    'Volume': 'float'
})

# Filter data by product name
df = df[df['Product Name'] == args.product_name]

# Sort by date
df.sort_values('Date', inplace=True)

# Handle missing values
df = df.ffill()

# Calculate 50-day moving average of Volume
df['Volume_50'] = df['Volume'].rolling(window=50, min_periods=1).mean()

# Calculate Volume Spike
df['Volume Spike'] = df['Volume'] > 1.5 * df['Volume_50']

# Filter data by the date of interest
date_of_interest = pd.to_datetime(args.date)
df_of_interest = df[df['Date'] == date_of_interest]

# Metrics to display for date of interest
if not df_of_interest.empty:
    avg_volume = df_of_interest['Volume_50'].values[0]
    volume_spike = df_of_interest['Volume Spike'].values[0]

    # Print metrics for average volume
    print(f"METRIC:Average Volume (Volume_50) VALUE:{avg_volume} UNIT:None TYPE:float")

    # Print metrics for volume spike
    print(f"METRIC:Volume Spike VALUE:{volume_spike} UNIT:None TYPE:boolean")

    # Current Volume vs Average Volume
    current_volume = df_of_interest['Volume'].values[0]
    print(f"METRIC:Current Volume VALUE:{current_volume} UNIT:None TYPE:float")
    print(f"METRIC:Volume vs. Average Volume VALUE:{current_volume / avg_volume} UNIT:Multiplier TYPE:float")

    # Example of volume changes, assuming major price movement identification (for demo purpose)
    # Assume major price movement days as placeholder condition
    price_movement_condition = (df['Close'] > df['Open'] * 1.05)
    price_movement_df = df[price_movement_condition & (df['Date'] <= date_of_interest)]

    if not price_movement_df.empty:
        significant_volume_change = price_movement_df['Volume'].mean() / df['Volume'].mean()
        print(f"METRIC:Volume changes during significant price movements VALUE:{significant_volume_change} UNIT:Multiplier TYPE:float")
