import pandas as pd
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, required=True)
parser.add_argument('--product_name', type=str, required=True)
parser.add_argument('--date', type=str, required=True)
args = parser.parse_args()

# Read data into DataFrame
df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Handle missing/invalid values
df.ffill(inplace=True)

# Filter by product name
product_df = df[df['Product Name'] == args.product_name]

# Calculate the current trading day's percentage change
current_day = pd.to_datetime(args.date)
current_data = product_df.loc[current_day]
current_open = current_data['Open']
current_close = current_data['Close']
percentage_change_current = (current_close - current_open) / current_open * 100

# Calculate the previous trading day's data
previous_day = current_day - pd.Timedelta(days=1)
previous_data = product_df.loc[previous_day]
previous_open = previous_data['Open']
previous_close = previous_data['Close']
percentage_change_previous = (previous_close - previous_open) / previous_open * 100

# Print results
print(f'METRIC:percentage_change_current\tVALUE:{percentage_change_current:.4f}\tUNIT:percent\tTYPE:float')
print(f'METRIC:percentage_change_previous\tVALUE:{percentage_change_previous:.4f}\tUNIT:percent\tTYPE:float')
