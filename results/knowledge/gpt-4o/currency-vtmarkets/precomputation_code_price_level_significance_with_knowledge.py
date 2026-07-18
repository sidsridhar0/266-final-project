import pandas as pd
import argparse

def process_data(df, product_name, date_of_interest):
    # Filter data for the specified product
    df = df[df['Product Name'] == product_name]

    # Ensure that date column is of datetime type
    df['Date'] = pd.to_datetime(df['Date'])

    # Sort data by date
    df.sort_values('Date', inplace=True)

    # Forward-fill to handle missing data
    df.ffill(inplace=True)

    # Determine historical highs and lows
    historical_highs = df['High'].max()
    historical_lows = df['Low'].min()

    # Current price at the date of interest
    current_price = df.loc[df['Date'] == date_of_interest, 'Close'].values[0]

    # Print metrics
    print(f"METRIC:historical_highs\tVALUE:{historical_highs}\tUNIT:price\tTYPE:float")
    print(f"METRIC:historical_lows\tVALUE:{historical_lows}\tUNIT:price\tTYPE:float")
    print(f"METRIC:current_price\tVALUE:{current_price}\tUNIT:price\tTYPE:float")

def main():
    parser = argparse.ArgumentParser(description='Price level significance calculations')
    parser.add_argument('--data_path', type=str, required=True, help='Path to data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product')
    parser.add_argument('--date', type=str, required=True, help='Date of interest')

    args = parser.parse_args()

    # Read the CSV file
    df = pd.read_csv(args.data_path, dtype={'Date': str, 'Product Name': str, 'Symbol': str, 
                                            'Open': float, 'High': float, 'Low': float, 
                                            'Close': float, 'Volume': float})
    
    # Process the data to calculate metrics
    process_data(df, args.product_name, args.date)

if __name__ == '__main__':
    main()
