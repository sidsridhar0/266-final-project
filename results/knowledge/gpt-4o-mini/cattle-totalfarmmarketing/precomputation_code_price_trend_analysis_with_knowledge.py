import pandas as pd
import argparse
import sys

# Setup command-line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, required=True)
parser.add_argument('--product_name', type=str, required=True)
parser.add_argument('--date', type=str, required=True)
args = parser.parse_args()

# Read data into pandas DataFrame
try:
    df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
except Exception as e:
    print(f"Error reading data: {e}")
    sys.exit(1)

# Convert data types
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Product Name'] = df['Product Name'].astype(str)
df['Symbol'] = df['Symbol'].astype(str)
df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
df['High'] = pd.to_numeric(df['High'], errors='coerce')
df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

# Handle missing/invalid values
df.ffill(inplace=True)

# Filter the DataFrame for the specific product and date range
product_data = df[(df['Product Name'] == args.product_name) & (df['Date'] <= pd.to_datetime(args.date))]

# Calculate metrics
if len(product_data) < 7:
    print("Not enough data to calculate trends.")
    sys.exit(1)

# Calculate 7-day closing average
product_data.set_index('Date', inplace=True)
closing_avg_7_days = product_data['Close'].rolling(window=7).mean().iloc[-1]

# Calculate current closing price and price from 7 days ago
current_close = product_data['Close'].iloc[-1]
closing_price_7_days_ago = product_data['Close'].iloc[-8] if len(product_data) >= 8 else None

# Calculate price trend change and percentage change
price_trend_change = current_close - closing_price_7_days_ago if closing_price_7_days_ago is not None else None
price_trend_percentage_change = (price_trend_change / closing_price_7_days_ago) * 100 if closing_price_7_days_ago else None

# Print results
print(f'METRIC:7-Day_Closing_Average\tVALUE:{closing_avg_7_days}\tUNIT:price\tTYPE:float')
print(f'METRIC:Current_Closing_Price\tVALUE:{current_close}\tUNIT:price\tTYPE:float')
if closing_price_7_days_ago is not None:
    print(f'METRIC:Price_Trend_Change\tVALUE:{price_trend_change}\tUNIT:price\tTYPE:float')
    print(f'METRIC:Price_Trend_Percentage_Change\tVALUE:{price_trend_percentage_change}\tUNIT:percent\tTYPE:float')
else:
    print('Not enough historical data for comparison to calculate Price_Trend_Change and Price_Trend_Percentage_Change.')
