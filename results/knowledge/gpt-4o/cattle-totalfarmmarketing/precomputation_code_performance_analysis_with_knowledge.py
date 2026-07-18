import pandas as pd
import argparse

# Initialize argument parser
parser = argparse.ArgumentParser(description='Process some cattle market data.')
parser.add_argument('--data_path', type=str, help='Path to the CSV data file')
parser.add_argument('--product_name', type=str, help='Name of the product to filter')
parser.add_argument('--date', type=str, help='Date of interest in YYYY-MM-DD format')
args = parser.parse_args()

# Read data
df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])

# Forward fill missing values
df.ffill(inplace=True)

# Convert columns to appropriate datatypes
df['Date'] = pd.to_datetime(df['Date'])
df['Open'] = df['Open'].astype(float)
df['High'] = df['High'].astype(float)
df['Low'] = df['Low'].astype(float)
df['Close'] = df['Close'].astype(float)
df['Volume'] = df['Volume'].astype(float)

# Filter by product name and sort by date
product_df = df[df['Product Name'] == args.product_name].sort_values(by='Date').reset_index(drop=True)

# Convert interest date to datetime
interest_date = pd.to_datetime(args.date)

# Calculate weekly change
product_df['Week'] = product_df['Date'].dt.to_period('W')
weekly_df = product_df.groupby('Week').last()
last_week_row = weekly_df[weekly_df.index == interest_date.to_period('W')]

if not last_week_row.empty:
    current_week_change = last_week_row['Close'].values[0] - product_df.loc[product_df['Week'] == last_week_row.index[0]].iloc[0]['Close']
    print(f"METRIC:current_week_change\tVALUE:{current_week_change}\tUNIT:\tTYPE:{type(current_week_change).__name__}")

# Calculate monthly change
product_df['Month'] = product_df['Date'].dt.to_period('M')
monthly_df = product_df.groupby('Month').last()
last_month_row = monthly_df[monthly_df.index == interest_date.to_period('M')]

if not last_month_row.empty:
    current_month_change = last_month_row['Close'].values[0] - product_df.loc[product_df['Month'] == last_month_row.index[0]].iloc[0]['Close']
    print(f"METRIC:current_month_change\tVALUE:{current_month_change}\tUNIT:\tTYPE:{type(current_month_change).__name__}")

# Calculate year-to-date change
year_start_row = product_df[product_df['Date'].dt.year == interest_date.year].sort_values(by='Date').head(1)

if not year_start_row.empty:
    year_to_date_change = product_df[product_df['Date'] <= interest_date].iloc[-1]['Close'] - year_start_row['Close'].values[0]
    print(f"METRIC:year_to_date_change\tVALUE:{year_to_date_change}\tUNIT:\tTYPE:{type(year_to_date_change).__name__}")
