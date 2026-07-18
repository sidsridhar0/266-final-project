import pandas as pd
import argparse

# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, required=True, help='Path to the data file')
parser.add_argument('--product_name', type=str, required=True, help='Name of the product')
parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
args = parser.parse_args()

# Read data into DataFrame
df = pd.read_csv(args.data_path)

# Select relevant columns
df = df[["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"]]

# Convert data types
df['Date'] = pd.to_datetime(df['Date'])
df['Open'] = df['Open'].astype(float)
df['High'] = df['High'].astype(float)
df['Low'] = df['Low'].astype(float)
df['Close'] = df['Close'].astype(float)
df['Volume'] = df['Volume'].astype(float)

# Handle missing/invalid values
df.ffill(inplace=True)

# Filter data for specific product
filtered_df = df[df["Product Name"] == args.product_name]

# Calculate Daily Range
filtered_df['Daily_Range'] = filtered_df['High'] - filtered_df['Low']

# Calculate Percentage Change
filtered_df['Percentage_Change'] = (filtered_df['Close'] - filtered_df['Open']) / filtered_df['Open'] * 100

# Get the date of interest data
date_of_interest = pd.to_datetime(args.date)
current_data = filtered_df[filtered_df['Date'] == date_of_interest]

# Calculate Average Daily Range over the last 30 days
avg_daily_range = filtered_df['Daily_Range'].tail(30).mean()

current_daily_range = current_data['Daily_Range'].values[0] if not current_data.empty else None
historical_percentage_change_avg = filtered_df['Percentage_Change'].mean()
current_percentage_change = current_data['Percentage_Change'].values[0] if not current_data.empty else None

# Print results in structured format
if not current_data.empty:
    print(f"METRIC:Daily_Range\tVALUE:{current_daily_range}\tUNIT:price\tTYPE:float")
    print(f"METRIC:Average_Daily_Range\tVALUE:{avg_daily_range}\tUNIT:price\tTYPE:float")
    print(f"METRIC:Percentage_Change\tVALUE:{current_percentage_change}\tUNIT:percent\tTYPE:float")
else:
    print("No data available for the specified product and date.")
