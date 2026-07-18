import pandas as pd
import argparse

def calculate_daily_volatility(df, date_of_interest):
    # Forward fill missing values
    df = df.ffill()

    # Calculate daily volatility
    df['daily_volatility'] = ((df['High'] - df['Low']) / df['Low']) * 100

    # Filter data by date of interest
    result = df[df['Date'] == date_of_interest]

    if not result.empty:
        daily_volatility_value = result.iloc[0]['daily_volatility']
        print("METRIC:daily_volatility")
        print(f"VALUE:{daily_volatility_value}")
        print("UNIT:percent")
        print("TYPE:float")
    else:
        print("No data available for the specified date.")

def main(args):
    # Read data from csv file
    df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])

    # Filter by product name
    df = df[df['Product Name'] == args.product_name]

    # Ensure correct data types
    df = df.astype({"Date": "str", "Product Name": "str", "Symbol": "str", "Open": "float", "High": "float", "Low": "float", "Close": "float", "Volume": "float"})

    # Calculate metrics
    calculate_daily_volatility(df, args.date)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate daily volatility for a given currency pair.")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the data CSV file")
    parser.add_argument("--product_name", type=str, required=True, help="Name of the product to analyze")
    parser.add_argument("--date", type=str, required=True, help="Date of interest in YYYY-MM-DD format")
    args = parser.parse_args()
    
    main(args)
