import pandas as pd
import argparse
import numpy as np
import sys

def read_and_process_data(data_path):
    try:
        data = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
        data.dropna(inplace=True)
        data["Date"] = pd.to_datetime(data["Date"], errors='coerce')
        data.dropna(subset=["Date"], inplace=True)
        return data
    except FileNotFoundError:
        print("File not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def support_resistance_levels(data, product_name, date, days=30):
    filtered_data = data[data['Product Name'] == product_name]
    filtered_data.set_index('Date', inplace=True)
    
    recent_data = filtered_data.loc[:date].tail(days)

    support_levels = recent_data.groupby('Low').size().reset_index(name='Frequency')
    resistance_levels = recent_data.groupby('High').size().reset_index(name='Frequency')

    significant_supports = support_levels[support_levels['Frequency'] > 1].sort_values(by=['Frequency', 'Low'], ascending=[False, True])
    significant_resistances = resistance_levels[resistance_levels['Frequency'] > 1].sort_values(by=['Frequency', 'High'], ascending=[False, True])

    return significant_supports, significant_resistances

def main(args):
    data = read_and_process_data(args.data_path)
    
    supports_30, resistances_30 = support_resistance_levels(data, args.product_name, args.date, 30)
    supports_60, resistances_60 = support_resistance_levels(data, args.product_name, args.date, 60)
    
    # Print Results
    if not supports_30.empty:
        for index, row in supports_30.iterrows():
            print(f"METRIC:support_levels_30 VALUE:{row['Low']} UNIT:price TYPE:float")

    if not resistances_30.empty:
        for index, row in resistances_30.iterrows():
            print(f"METRIC:resistance_levels_30 VALUE:{row['High']} UNIT:price TYPE:float")
            
    if not supports_60.empty:
        for index, row in supports_60.iterrows():
            print(f"METRIC:support_levels_60 VALUE:{row['Low']} UNIT:price TYPE:float")

    if not resistances_60.empty:
        for index, row in resistances_60.iterrows():
            print(f"METRIC:resistance_levels_60 VALUE:{row['High']} UNIT:price TYPE:float")

    # Frequency of touch
    frequency_touch = pd.concat([supports_30, resistances_30, supports_60, resistances_60]).groupby("Frequency").size()
    for freq, count in frequency_touch.items():
        print(f"METRIC:frequency_of_touch VALUE:{freq} UNIT:counts TYPE:int")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate support and resistance levels.')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the data file')
    parser.add_argument('--product_name', type=str, required=True, help='Product name to analyze')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')

    args = parser.parse_args()
    main(args)
