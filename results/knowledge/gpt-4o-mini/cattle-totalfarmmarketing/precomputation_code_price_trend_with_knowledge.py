import pandas as pd
import argparse

def main(data_path, product_name, date):
    # Read data into pandas DataFrame
    df = pd.read_csv(data_path, dtype={
        "Date": str,
        "Product Name": str,
        "Symbol": str,
        "Open": float,
        "High": float,
        "Low": float,
        "Close": float,
        "Volume": float
    })

    # Handle missing/invalid values
    df = df.ffill()

    # Convert date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Filter for the specified product
    df = df[df['Product Name'] == product_name]

    # Sort by date
    df = df.sort_values(by='Date')

    # Creating metrics
    df['percentage_change'] = df['Close'].pct_change() * 100
    df['closing_price_yesterday'] = df['Close'].shift(1)

    # Filter data for the specified date
    date_of_interest = pd.to_datetime(date)
    filtered_df = df[df['Date'] == date_of_interest]

    # Get the previous day data
    previous_day_data = df[df['Date'] < date_of_interest].iloc[-1]

    # Prepare output
    if not filtered_df.empty:
        current_data = filtered_df.iloc[0]
        percentage_change = current_data['percentage_change']
        closing_price_yesterday = previous_day_data['Close']

        print(f"METRIC:percentage_change\tVALUE:{percentage_change:.4f}\tUNIT:percent\tTYPE:float")
        print(f"METRIC:closing_price_yesterday\tVALUE:{closing_price_yesterday:.4f}\tUNIT:currency\tTYPE:float")
    else:
        print("No data available for the specified date.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some financial data.')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')

    args = parser.parse_args()
    main(args.data_path, args.product_name, args.date)
