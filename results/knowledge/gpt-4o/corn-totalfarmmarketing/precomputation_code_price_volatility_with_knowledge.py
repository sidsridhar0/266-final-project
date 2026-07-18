import pandas as pd
import argparse

def calculate_true_range(data):
    data['Previous Close'] = data['Close'].shift(1)
    data['High-Low'] = data['High'] - data['Low']
    data['High-Previous Close'] = (data['High'] - data['Previous Close']).abs()
    data['Low-Previous Close'] = (data['Low'] - data['Previous Close']).abs()

    data['True Range'] = data[['High-Low', 'High-Previous Close', 'Low-Previous Close']].max(axis=1)
    return data

def calculate_atr(data, period=14):
    data['ATR'] = data['True Range'].rolling(window=period, min_periods=1).mean()
    return data

def handle_missing_values(data):
    data = data.bfill().ffill()
    return data

def main(data_path, product_name, date_of_interest):
    data = pd.read_csv(data_path, parse_dates=['Date'], dtype={
        "Product Name": "str", 
        "Symbol": "str", 
        "Open": "float", 
        "High": "float", 
        "Low": "float", 
        "Close": "float", 
        "Volume": "float"
    })

    data['Date'] = pd.to_datetime(data['Date'])
    data = data[data['Product Name'] == product_name]

    data = handle_missing_values(data)

    data = calculate_true_range(data)
    data = calculate_atr(data)

    date_filtered_data = data[data['Date'] == pd.to_datetime(date_of_interest)]
    
    if not date_filtered_data.empty:
        atr_value = date_filtered_data['ATR'].values[0]
        true_range_value = date_filtered_data['True Range'].values[0]

        print(f"METRIC:True Range\tVALUE:{true_range_value}\tUNIT:points\tTYPE:float")
        print(f"METRIC:ATR\tVALUE:{atr_value}\tUNIT:points\tTYPE:float")
    else:
        print(f"No data available for {product_name} on {date_of_interest}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate ATR and True Range')
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()
    
    main(args.data_path, args.product_name, args.date)
