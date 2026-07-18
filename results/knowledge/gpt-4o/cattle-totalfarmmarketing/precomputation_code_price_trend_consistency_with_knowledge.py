import pandas as pd
import argparse
from datetime import datetime, timedelta

# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, required=True,
                    help='Path to the CSV data file')
parser.add_argument('--product_name', type=str, required=True,
                    help='Name of the product to analyze')
parser.add_argument('--date', type=str, required=True,
                    help='The date of interest in YYYY-MM-DD format')

# Read arguments
args = parser.parse_args()
data_path = args.data_path
product_name = args.product_name
date_of_interest = args.date

# Read data
df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Close"],
                 dtype={"Date": str, "Product Name": str, "Close": float})

# Convert Date to datetime and sort
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values('Date', inplace=True)

# Filter the data for the specific product name
df = df[df['Product Name'] == product_name]

# Determine date range: last 90 days before the given date
end_date = datetime.strptime(date_of_interest, "%Y-%m-%d")
start_date = end_date - timedelta(days=90)

# Filter data further to the past 90 days
df_filtered = df[(df['Date'] <= end_date) & (df['Date'] > start_date)]

# Calculate up_days and down_days
df_filtered['previous_close'] = df_filtered['Close'].shift(1)

# Handle missing values for previous_close
df_filtered.dropna(inplace=True)

up_days = (df_filtered['Close'] > df_filtered['previous_close']).sum()
down_days = (df_filtered['Close'] < df_filtered['previous_close']).sum()
total_days = len(df_filtered)

# Calculate trend consistency ratio
trend_consistency_ratio = up_days / total_days if total_days > 0 else 0

# Print results
print("METRIC:up_days\tVALUE:{}\tUNIT:days\tTYPE:int".format(up_days))
print("METRIC:down_days\tVALUE:{}\tUNIT:days\tTYPE:int".format(down_days))
print("METRIC:trend_consistency_ratio\tVALUE:{:.4f}\tUNIT:ratio\tTYPE:float".format(trend_consistency_ratio))
