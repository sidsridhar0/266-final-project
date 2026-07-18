import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse

def calculate_RSI(series, periods=14):
    delta = series.diff(1).dropna()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI

def momentum_analysis(data_path, product_name, date):
    # Load data
    data = pd.read_csv(data_path)

    # Ensure data types
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

    # Filter the data for the product
    product_data = data[data["Product Name"] == product_name].copy()

    # Calculate RSI for each date
    product_data['RSI'] = calculate_RSI(product_data['Close'])

    # Calculate average RSI over the past month (30 days)
    product_data = product_data.dropna(subset=['RSI'])
    product_data['avg_RSI_30_days'] = product_data['RSI'].rolling(window=30).mean()

    # Identify momentum signals
    product_data['momentum_signal'] = np.where(product_data['RSI'] > 70, 'overbought',
                                               np.where(product_data['RSI'] < 30, 'oversold', 'neutral'))

    # Filter data up to the specified date
    date_of_interest = datetime.strptime(date, "%Y-%m-%d")
    final_data = product_data[product_data['Date'] <= date_of_interest].copy()

    # Extract the latest data point
    if not final_data.empty:
        latest_row = final_data.iloc[-1]

        # Print results
        print(f"METRIC:RSI\tVALUE:{latest_row['RSI']}\tUNIT:\tTYPE:float")
        print(f"METRIC:average_RSI\tVALUE:{latest_row['avg_RSI_30_days']}\tUNIT:\tTYPE:float")
        print(f"METRIC:momentum_signal\tVALUE:{latest_row['momentum_signal']}\tUNIT:\tTYPE:str")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()

    momentum_analysis(args.data_path, args.product_name, args.date)
