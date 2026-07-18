import pandas as pd
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV data file')
parser.add_argument('--product_name', type=str, required=True, help='Product name to analyze')
parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
args = parser.parse_args()

# Read data into a DataFrame
df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
df['Date'] = pd.to_datetime(df['Date'])
df['Volume'] = df['Volume'].astype(float)

# Filter for specific product
df = df[df['Product Name'] == args.product_name]

# Handle missing values
df.ffill(inplace=True)

# Calculate the Current Volume for the date of interest
date_of_interest = pd.to_datetime(args.date)
current_volume = df[df['Date'] == date_of_interest]['Volume'].values[0] if not df[df['Date'] == date_of_interest].empty else 0.0

# Calculate the Average Volume over the past 30 days
average_volume_30d = df[df['Date'] < date_of_interest].set_index('Date')['Volume'].rolling(window='30D').mean().iloc[-1] if (df['Date'] < date_of_interest).any() else 0.0

# Calculate Volume Change Percentage
volume_change_percentage = ((current_volume - average_volume_30d) / average_volume_30d * 100) if average_volume_30d != 0 else 0.0

# Print results
metrics = {
    "Current_Volume": current_volume,
    "Average_Volume_30d": average_volume_30d,
    "Volume_Change_Percentage": volume_change_percentage,
}

for metric_name, value in metrics.items():
    print(f'METRIC:{metric_name}\tVALUE:{value:.4f}\tUNIT:{"volume" if "Volume" in metric_name else "percent"}\tTYPE:{"float" if isinstance(value, float) else "unknown"}')
