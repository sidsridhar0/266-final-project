import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(description='Volume Analysis Script')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the data CSV file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product to analyze')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.data_path, dtype={
        "Date": "str",
        "Product Name": "str",
        "Symbol": "str",
        "Open": "float",
        "High": "float",
        "Low": "float",
        "Close": "float",
        "Volume": "float"
    })
    
    # Filter by product
    df = df[df['Product Name'] == args.product_name]
    
    # Convert Date to datetime for easier filtering and sorting
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Sort by date
    df.sort_values('Date', inplace=True)
    
    # Calculate the 14-day average volume
    df['average_volume'] = df['Volume'].rolling(window=14, min_periods=1).mean()
    
    # Filtering for relevant dates (at least two weeks data for calculations)
    data_of_interest = df[df['Date'] <= pd.to_datetime(args.date)]
    
    # Get the record of the date of interest
    doi_record = data_of_interest[data_of_interest['Date'] == pd.to_datetime(args.date)]
    
    if not doi_record.empty:
        avg_volume = doi_record.iloc[0]['average_volume']
        volume_on_date = doi_record.iloc[0]['Volume']
        
        # Calculate volume change and percentage volume change
        volume_change = volume_on_date - avg_volume
        percentage_volume_change = (volume_change / avg_volume) * 100
        
        # Print the results
        print(f"METRIC:average_volume\tVALUE:{avg_volume:.2f}\tUNIT:units\tTYPE:float")
        print(f"METRIC:volume_change\tVALUE:{volume_change:.2f}\tUNIT:units\tTYPE:float")
        print(f"METRIC:percentage_volume_change\tVALUE:{percentage_volume_change:.2f}\tUNIT:percent\tTYPE:float")
    else:
        print("No data available for the date of interest")

if __name__ == "__main__":
    main()
