import argparse
import pandas as pd

def calculate_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
            obv.append(obv[i - 1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
            obv.append(obv[i - 1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[i - 1])
    return obv

def calculate_volume_spike(df, date_of_interest):
    average_volume = df['Volume'].rolling(window=20, min_periods=1).mean()
    current_volume = df.loc[df['Date'] == date_of_interest, 'Volume'].values[0]
    avg_volume_last_20 = average_volume.loc[df['Date'] == date_of_interest].values[0]
    volume_change = current_volume / avg_volume_last_20 if avg_volume_last_20 != 0 else 0
    return volume_change

def main(data_path, product_name, date_of_interest):
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

    # Filter for the specified product
    df = df[df['Product Name'] == product_name].copy()
    
    # Forward fill missing values
    df.ffill(inplace=True)

    # Calculate OBV
    df['OBV'] = calculate_obv(df)

    # Calculate volume change/spike
    volume_change = calculate_volume_spike(df, date_of_interest)

    # Get the latest OBV
    latest_obv = df.loc[df['Date'] == date_of_interest, 'OBV'].values[0]

    # Display results
    print(f"METRIC:OBV\tVALUE:{latest_obv}\tUNIT:\tTYPE:float")
    print(f"METRIC:Volume Change\tVALUE:{volume_change}\tUNIT:\tTYPE:float")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Volume Analysis')
    parser.add_argument('--data_path', type=str, required=True, help='Path to CSV data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of Product')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
    args = parser.parse_args()

    main(args.data_path, args.product_name, args.date)
