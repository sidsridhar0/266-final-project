import pandas as pd
import argparse

def calculate_volume_analysis(data_path, product_name, date_of_interest):
    # Load data
    df = pd.read_csv(data_path, parse_dates=['Date'], dtype={
        "Date": "str",
        "Product Name": "str",
        "Symbol": "str",
        "Open": "float",
        "High": "float",
        "Low": "float",
        "Close": "float",
        "Volume": "float"
    })

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')
    
    # Forward fill missing values
    df = df.ffill()

    product_data = df[df['Product Name'] == product_name]
    product_data.set_index('Date', inplace=True)

    # Calculate average volume before filtering for date of interest
    product_data['average_volume'] = product_data['Volume'].rolling(window=30, min_periods=1).mean()

    # Ensure date_of_interest is a datetime object for correct comparison
    date_of_interest = pd.to_datetime(date_of_interest)

    if date_of_interest not in product_data.index:
        print("Date of interest not found in the data.")
        return

    volume_of_interest = product_data.loc[date_of_interest, 'Volume']
    average_volume_of_interest = product_data.loc[date_of_interest, 'average_volume']

    if pd.isna(average_volume_of_interest):
        print("Insufficient data to calculate average volume for the date of interest.")
        return

    if average_volume_of_interest == 0:
        print("Average volume is zero, cannot compute percentage change.")
        return

    volume_change_percentage = ((volume_of_interest - average_volume_of_interest) / average_volume_of_interest) * 100

    print(f"METRIC:average_volume\tVALUE:{average_volume_of_interest}\tUNIT:none\tTYPE:float")
    print(f"METRIC:volume_change_percentage\tVALUE:{volume_change_percentage}\tUNIT:percent\tTYPE:float")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Volume Analysis')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV file containing trading data')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product to analyze')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
    args = parser.parse_args()

    calculate_volume_analysis(args.data_path, args.product_name, args.date)
