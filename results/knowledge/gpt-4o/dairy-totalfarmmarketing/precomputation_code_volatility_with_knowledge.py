import pandas as pd
import argparse

def calculate_and_print_market_volatility(data_path, product_name, date_of_interest):
    # Read data
    dtype_spec = {"Date": "str", "Product Name": "str", "Symbol": "str", "Open": "float", "High": "float", "Low": "float", "Close": "float", "Volume": "float"}
    df = pd.read_csv(data_path, dtype=dtype_spec)
    
    # Fill missing values
    df = df.ffill()

    # Filter for the selected product
    df = df[df["Product Name"] == product_name]
    
    # Ensure data is sorted by date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')

    # Calculating True Range (TR)
    df["Previous Close"] = df["Close"].shift(1)
    df["High_Low"] = df["High"] - df["Low"]
    df["High_PreviousClose"] = (df["High"] - df["Previous Close"]).abs()
    df["Low_PreviousClose"] = (df["Low"] - df["Previous Close"]).abs()
    df["True Range"] = df[["High_Low", "High_PreviousClose", "Low_PreviousClose"]].max(axis=1)

    # Calculate 14-day ATR
    df["ATR_14"] = df["True Range"].rolling(window=14).mean()

    # Calculate Historical Average ATR
    historical_average_atr = df["ATR_14"].mean()

    # Filter by the date of interest after calculating metrics
    df_filtered = df[df['Date'] <= pd.to_datetime(date_of_interest)]

    # Get the latest ATR and necessary values on the date of interest
    latest_row = df_filtered.iloc[-1]
    current_atr = latest_row["ATR_14"]
    current_close = latest_row["Close"]

    # Print the required metrics
    print("METRIC:Current ATR VALUE:{} UNIT:None TYPE:float".format(current_atr))
    print("METRIC:Historical Average ATR VALUE:{} UNIT:None TYPE:float".format(historical_average_atr))
    print("METRIC:Latest Close VALUE:{} UNIT:None TYPE:float".format(current_close))
    
    # Comparison: Current ATR vs Historical Average ATR
    print("METRIC:Current ATR vs Historical Average ATR VALUE:{} UNIT:None TYPE:float".format(current_atr - historical_average_atr))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate market volatility metrics.')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
    args = parser.parse_args()

    calculate_and_print_market_volatility(args.data_path, args.product_name, args.date)
