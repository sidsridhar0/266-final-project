import pandas as pd
import argparse

def calculate_volatility_analysis(data_path, product_name, date):
    # Read data
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "High", "Low"], parse_dates=["Date"])
    
    # Forward fill missing data
    df = df.ffill()
    
    # Filter data for the given product name
    df = df[df["Product Name"] == product_name]
    
    # Calculate daily price range
    df["daily_price_range"] = df["High"] - df["Low"]
    
    # Calculate dates
    date_of_interest = pd.to_datetime(date)
    start_date_week = date_of_interest - pd.Timedelta(days=6)
    start_date_month = date_of_interest - pd.Timedelta(days=29)
    
    # Maintain historical data for calculation
    df_week = df[(df["Date"] >= start_date_week) & (df["Date"] <= date_of_interest)]
    df_month = df[(df["Date"] >= start_date_month) & (df["Date"] <= date_of_interest)]
    
    # Calculate average weekly and monthly price range
    avg_weekly_price_range = df_week["daily_price_range"].mean()
    avg_monthly_price_range = df_month["daily_price_range"].mean()
    
    # Retrieve the daily price range for the specified date
    daily_price_range = df[df["Date"] == date_of_interest]["daily_price_range"].iloc[0]
    
    # Print results in structured format
    print(f"METRIC:daily_price_range VALUE:{daily_price_range} UNIT:None TYPE:float")
    print(f"METRIC:avg_weekly_price_range VALUE:{avg_weekly_price_range} UNIT:None TYPE:float")
    print(f"METRIC:avg_monthly_price_range VALUE:{avg_monthly_price_range} UNIT:None TYPE:float")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()
    
    calculate_volatility_analysis(args.data_path, args.product_name, args.date)
