import argparse
import pandas as pd

def main(data_path, product_name, date):
    # Read data into DataFrame
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    
    # Convert date column to datetime and other necessary columns to appropriate types
    df['Date'] = pd.to_datetime(df['Date'])
    df['Open'] = df['Open'].astype(float)
    df['Close'] = df['Close'].astype(float)

    # Handle missing/invalid values
    df.ffill(inplace=True)

    # Filter data for the given product name
    df = df[df['Product Name'] == product_name]

    # Sort by date
    df = df.sort_values('Date')
    
    # Calculate the closing price change relative to opening price for the past 7 days
    df['Close_Open_Change'] = df['Close'] - df['Open']
    
    # Get data for the last 7 days relative to the date of interest
    target_date = pd.to_datetime(date)
    past_week_data = df[(df['Date'] < target_date) & (df['Date'] >= target_date - pd.Timedelta(days=7))]

    if past_week_data.empty:
        print("No data available for the specified date range.")
        return

    # Calculate weekly metrics
    total_days = past_week_data.shape[0]
    days_closed_higher = (past_week_data['Close_Open_Change'] > 0).sum()
    days_closed_lower = (past_week_data['Close_Open_Change'] < 0).sum()

    percentage_higher = (days_closed_higher / total_days) * 100 if total_days > 0 else 0
    percentage_lower = (days_closed_lower / total_days) * 100 if total_days > 0 else 0

    # Overall trend direction based on change
    overall_trend = past_week_data['Close_Open_Change'].sum()
    
    # Print results
    print(f"METRIC:weekly_close_open_change")
    print(f"VALUE:{overall_trend}")
    print(f"UNIT:currency")
    print(f"TYPE:float")
    
    print(f"METRIC:days_closed_higher_percentage")
    print(f"VALUE:{percentage_higher}")
    print(f"UNIT:percent")
    print(f"TYPE:float")
    
    print(f"METRIC:days_closed_lower_percentage")
    print(f"VALUE:{percentage_lower}")
    print(f"UNIT:percent")
    print(f"TYPE:float")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()
    
    main(args.data_path, args.product_name, args.date)
