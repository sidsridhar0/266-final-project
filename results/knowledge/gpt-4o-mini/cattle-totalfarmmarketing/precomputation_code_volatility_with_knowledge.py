import pandas as pd
import argparse

def calculate_atr(df):
    df['Previous Close'] = df['Close'].shift(1)
    df['TR'] = df[['High', 'Low', 'Previous Close']].apply(
        lambda x: max(x['High'] - x['Low'], abs(x['High'] - x['Previous Close']), abs(x['Low'] - x['Previous Close'])), axis=1
    )
    atr_14 = df['TR'].rolling(window=14).mean().iloc[-1]
    return atr_14

def calculate_std_dev_close(df):
    std_dev_close_14 = df['Close'].rolling(window=14).std().iloc[-1]
    return std_dev_close_14

def main(data_path, product_name, date):
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(float)

    df.ffill(inplace=True)
    
    # Filter by product name and date of interest
    df = df[(df['Product Name'] == product_name) & (df['Date'] <= pd.to_datetime(date))]

    # Calculate metrics
    atr_14 = calculate_atr(df)
    std_dev_close_14 = calculate_std_dev_close(df)

    # Prepare and print results
    metrics = {
        "ATR_14": atr_14,
        "std_dev_close_14": std_dev_close_14
    }

    for metric_name, value in metrics.items():
        print(f"METRIC:{metric_name}\tVALUE:{value:.4f}\tUNIT:None\tTYPE:{type(value).__name__}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument("--product_name", type=str, required=True)
    parser.add_argument("--date", type=str, required=True)
    args = parser.parse_args()
    
    main(args.data_path, args.product_name, args.date)
