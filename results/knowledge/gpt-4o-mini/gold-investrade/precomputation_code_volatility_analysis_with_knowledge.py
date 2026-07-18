import pandas as pd
import argparse

def calculate_volatility(data_path, product_name, date):
    df = pd.read_csv(data_path, parse_dates=['Date'])
    
    # Filter the relevant columns
    df = df[["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"]]
    
    # Handle missing/invalid values
    df.ffill(inplace=True)
    
    # Ensure the correct types
    df["High"] = df["High"].astype(float)
    df["Low"] = df["Low"].astype(float)
    df["Close"] = df["Close"].astype(float)
    
    # Sort data by date
    df.sort_values(by="Date", inplace=True)
    
    # Filter for the specific product
    product_data = df[df["Product Name"] == product_name]

    # Calculate daily price range
    product_data['daily_price_range'] = product_data['High'] - product_data['Low']
    
    # Calculate the standard deviation of the last 30 days' closing prices
    product_data['30_day_std_dev'] = product_data['Close'].rolling(window=30).std()
    
    # Filter by the date of interest and previous 30 days
    date_of_interest = pd.to_datetime(date)
    current_data = product_data[product_data['Date'] <= date_of_interest]
    
    # Get the most recent values for metrics
    current_daily_range = current_data['daily_price_range'].iloc[-1] if not current_data.empty else None
    current_std_dev = current_data['30_day_std_dev'].iloc[-1] if not current_data.empty else None

    # Historical averages calculations
    historical_daily_range_avg = product_data['daily_price_range'].mean() if not product_data.empty else None
    historical_std_dev_avg = product_data['30_day_std_dev'].mean() if not product_data.empty else None

    # Print results
    print(f'METRIC:daily_price_range\tVALUE:{current_daily_range}\tUNIT:USD\tTYPE:float')
    print(f'METRIC:30_day_std_dev\tVALUE:{current_std_dev}\tUNIT:USD\tTYPE:float')
    print(f'METRIC:historical_daily_range_avg\tVALUE:{historical_daily_range_avg}\tUNIT:USD\tTYPE:float')
    print(f'METRIC:historical_std_dev_avg\tVALUE:{historical_std_dev_avg}\tUNIT:USD\tTYPE:float')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()
    
    calculate_volatility(args.data_path, args.product_name, args.date)
