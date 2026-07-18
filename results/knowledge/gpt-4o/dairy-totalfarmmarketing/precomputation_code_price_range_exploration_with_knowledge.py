import pandas as pd
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Analyze OHLC data for market sentiment')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the input data file')
    parser.add_argument('--product_name', type=str, required=True, help='The product name to analyze')
    parser.add_argument('--date', type=str, required=True, help='The date of interest')
    args = parser.parse_args()

    # Read data from CSV file
    data = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    
    # Forward fill missing values as specified
    data = data.ffill()

    # Convert columns to appropriate data types
    data["Date"] = pd.to_datetime(data["Date"])
    data[["Open", "High", "Low", "Close", "Volume"]] = data[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    # Filter data for the specific product name and date
    specific_data = data[(data["Product Name"] == args.product_name) & (data["Date"] == args.date)]
    
    if specific_data.empty:
        print(f"No data found for product {args.product_name} on date {args.date}")
        return

    # Calculate required metrics
    candle_data = specific_data.iloc[0]
    open_price = candle_data["Open"]
    close_price = candle_data["Close"]
    high_price = candle_data["High"]
    low_price = candle_data["Low"]

    # Daily Candle Representation
    print(f"METRIC:Daily Candle\tVALUE:OHLC({open_price}, {high_price}, {low_price}, {close_price})\tUNIT:N/A\tTYPE:string")

    # Body Size
    body_size = abs(open_price - close_price)
    print(f"METRIC:Body Size\tVALUE:{body_size}\tUNIT:dollars\tTYPE:float")

    # Wick Size
    upper_wick = high_price - max(open_price, close_price)
    lower_wick = min(open_price, close_price) - low_price
    print(f"METRIC:Upper Wick Size\tVALUE:{upper_wick}\tUNIT:dollars\tTYPE:float")
    print(f"METRIC:Lower Wick Size\tVALUE:{lower_wick}\tUNIT:dollars\tTYPE:float")

if __name__ == '__main__':
    main()
