import pandas as pd
import numpy as np
import argparse

def calculate_RSI(data, periods=14):
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=periods, min_periods=periods).mean()
    avg_loss = pd.Series(loss).rolling(window=periods, min_periods=periods).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_stochastic_oscillator(data, periods=14):
    low_min = data['Low'].rolling(window=periods).min()
    high_max = data['High'].rolling(window=periods).max()

    stochastic_oscillator = ((data['Close'] - low_min) / (high_max - low_min)) * 100
    
    return stochastic_oscillator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    
    args = parser.parse_args()
    
    df = pd.read_csv(args.data_path, dtype={
        "Date": "str", "Product Name": "str", "Symbol": "str",
        "Open": "float", "High": "float", "Low": "float",
        "Close": "float", "Volume": "float"
    })
    
    df = df.ffill()
    df = df[df['Product Name'] == args.product_name]
    df['Date'] = pd.to_datetime(df['Date'])
    
    df.sort_values('Date', inplace=True)

    rsi = calculate_RSI(df)
    stoch_osc = calculate_stochastic_oscillator(df)
    
    date_of_interest = pd.to_datetime(args.date)
    result_date_data = df[df['Date'] == date_of_interest]

    rsi_value = rsi[result_date_data.index[0]]
    stoch_osc_value = stoch_osc[result_date_data.index[0]]

    if not np.isnan(rsi_value):
        print(f"METRIC:RSI VALUE:{rsi_value:.2f} UNIT:integer TYPE:float")
    else:
        print("METRIC:RSI VALUE:N/A UNIT:integer TYPE:float")
    
    if not np.isnan(stoch_osc_value):
        print(f"METRIC:stochastic_oscillator VALUE:{stoch_osc_value:.2f} UNIT:integer TYPE:float")
    else:
        print("METRIC:stochastic_oscillator VALUE:N/A UNIT:integer TYPE:float")

if __name__ == "__main__":
    main()
