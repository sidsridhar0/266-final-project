import pandas as pd
import numpy as np
import argparse

def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def main(data_path, product_name, date):
    df = pd.read_csv(data_path, parse_dates=['Date'], dtype={
        "Date": str,
        "Product Name": str,
        "Symbol": str,
        "Open": float,
        "High": float,
        "Low": float,
        "Close": float,
        "Volume": float
    })

    df.ffill(inplace=True)

    df = df[(df['Product Name'] == product_name)]
    df.set_index('Date', inplace=True)
    
    rsi_14 = calculate_rsi(df['Close'])
    df['RSI_14'] = rsi_14
    
    if date not in df.index:
        raise ValueError("Date not found in dataset.")
    
    current_data = df.loc[date]
    current_close = current_data['Close']
    current_rsi = current_data['RSI_14']
    
    metrics = {
        "RSI_14": current_rsi,
        "current_close": current_close
    }
    
    for metric, value in metrics.items():
        print(f"METRIC:{metric}\tVALUE:{value:.4f}\tUNIT:\tTYPE:{type(value).__name__}")

    overbought = current_rsi > 70
    oversold = current_rsi < 30

    if overbought:
        print("Market indicates overbought conditions.")
    elif oversold:
        print("Market indicates oversold conditions.")
    else:
        print("Market is neither overbought nor oversold.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()
    
    main(args.data_path, args.product_name, args.date)
