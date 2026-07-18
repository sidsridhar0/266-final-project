import pandas as pd
from argparse import ArgumentParser
from sklearn.linear_model import LinearRegression
import numpy as np

def main(data_path, product_name, date):
    # Load the data
    df = pd.read_csv(data_path, parse_dates=['Date'])

    # Filter the DataFrame for the specified product
    df = df[df['Product Name'] == product_name]

    # Ensure correct data types
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(float)

    # Forward fill missing values
    df = df.ffill()

    # Assume interested date is in 'YYYY-MM-DD' format
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.Timedelta(days=19)

    # Calculate 20-day average volume
    average_volume = df.loc[(df['Date'] <= end_date) & (df['Date'] >= start_date), 'Volume'].mean()
    
    # Calculate volume trend using Linear Regression
    recent_data = df.loc[df['Date'] <= end_date].copy()  # Only consider up to end_date for trending
    recent_data['Date_ordinal'] = recent_data['Date'].map(pd.Timestamp.toordinal)

    # Linear Regression for volume
    X = recent_data[['Date_ordinal']].values
    y_vol = recent_data['Volume'].values
    model_vol = LinearRegression().fit(X, y_vol)
    volume_trend = model_vol.coef_[0]

    # Print results
    print(f"METRIC:average_volume\tVALUE:{average_volume}\tUNIT:units\tTYPE:float")
    print(f"METRIC:volume_trend\tVALUE:{volume_trend}\tUNIT:units per day\tTYPE:float")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()
    main(args.data_path, args.product_name, args.date)
