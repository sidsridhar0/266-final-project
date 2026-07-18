import pandas as pd
import argparse
from datetime import datetime

def calculate_roc(data, n):
    data['ROC'] = ((data['Close'] - data['Close'].shift(n)) / data['Close'].shift(n)) * 100
    return data

def calculate_rsi(data, period):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def main(data_path, product_name, date_of_interest):
    # Read data
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"], parse_dates=['Date'])
    
    # Filter by product name and sort by date
    df = df[df['Product Name'] == product_name].sort_values(by='Date')

    # Calculate Rate of Change (ROC) for a 10-day period
    df = calculate_roc(df, 10)

    # Calculate Relative Strength Index (RSI) for a 14-day period
    df = calculate_rsi(df, 14)
    
    # Find the data only for the date of interest
    specific_date_data = df[df['Date'] == datetime.strptime(date_of_interest, "%Y-%m-%d")]
    
    # Handle missing values
    specific_date_data = specific_date_data.dropna()

    # Print ROC
    if 'ROC' in specific_date_data.columns and not specific_date_data.empty:
        print(f"METRIC:Rate of Change (ROC)\tVALUE:{specific_date_data.iloc[0]['ROC']}\tUNIT:percent\tTYPE:float")

    # Print RSI
    if 'RSI' in specific_date_data.columns and not specific_date_data.empty:
        print(f"METRIC:Relative Strength Index (RSI)\tVALUE:{specific_date_data.iloc[0]['RSI']}\tUNIT:index\tTYPE:float")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()

    main(args.data_path, args.product_name, args.date)
