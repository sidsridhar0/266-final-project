import pandas as pd
import numpy as np
import argparse
from datetime import datetime

def calculate_rsi(df, periods=14):
    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain_df = pd.Series(gain).rolling(window=periods, min_periods=1).mean()
    loss_df = pd.Series(loss).rolling(window=periods, min_periods=1).mean()

    rs = gain_df / loss_df
    rsi = 100 - (100 / (1 + rs))

    return rsi

def process_data(data_path, product_name, date):
    # Load data
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    df = df.dropna()
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df.ffill(inplace=True)

    # Filter by product
    df = df[df['Product Name'] == product_name]

    # Calculate RSI
    df['RSI'] = calculate_rsi(df)
    
    # Get the row of the specific date of interest
    date_of_interest = datetime.strptime(date, '%Y-%m-%d')
    df_of_interest = df[df['Date'] <= date_of_interest].iloc[-1]

    # Results output for RSI
    rsi_value = df_of_interest['RSI']
    print("METRIC:RSI\tVALUE:{:.4f}\tUNIT:\tTYPE:float".format(rsi_value))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, help='Path to the CSV file containing data.')
    parser.add_argument('--product_name', type=str, help='Name of the product to analyze.')
    parser.add_argument('--date', type=str, help='Date of interest in YYYY-MM-DD format.')
    args = parser.parse_args()

    process_data(args.data_path, args.product_name, args.date)

if __name__ == "__main__":
    main()
