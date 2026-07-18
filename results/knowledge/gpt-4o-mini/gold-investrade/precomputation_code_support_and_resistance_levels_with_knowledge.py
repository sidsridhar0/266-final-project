import pandas as pd
import argparse

def main(data_path, product_name, date_of_interest):
    # Read data from CSV
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"], 
                     dtype={"Date": str, "Product Name": str, "Symbol": str, "Open": float, 
                            "High": float, "Low": float, "Close": float, "Volume": float})
    
    # Handle missing/invalid values
    df.ffill(inplace=True)

    # Convert 'Date' to datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Filter by product name
    df = df[df['Product Name'] == product_name]

    # Sort by date
    df.sort_values('Date', inplace=True)

    # Calculate the support level
    past_30_days = df[df['Date'] >= (pd.to_datetime(date_of_interest) - pd.Timedelta(days=30))]
    support_level = past_30_days['Low'].min()
    
    # Calculate the resistance level
    resistance_level = past_30_days['High'].max()

    # Get the closing price on the date of interest
    closing_price = df[df['Date'] == pd.to_datetime(date_of_interest)]['Close'].values[0] if not df[df['Date'] == pd.to_datetime(date_of_interest)].empty else None

    # Print results
    print(f"METRIC:support_level\tVALUE:{support_level}\tUNIT:price\tTYPE:float")
    print(f"METRIC:resistance_level\tVALUE:{resistance_level}\tUNIT:price\tTYPE:float")
    if closing_price is not None:
        print(f"METRIC:closing_price\tVALUE:{closing_price}\tUNIT:price\tTYPE:float")
    else:
        print("Closing price not available for the specified date.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()

    main(args.data_path, args.product_name, args.date)
