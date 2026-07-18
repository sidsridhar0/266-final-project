import pandas as pd
import argparse

def calculate_trend(series):
    if series.is_monotonic_increasing:
        return 'up'
    elif series.is_monotonic_decreasing:
        return 'down'
    else:
        return 'sideways'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Open'] = df['Open'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(float)

    df = df.ffill()

    last_week_data = df[(df['Product Name'] == args.product_name) & (df['Date'] >= (pd.to_datetime(args.date) - pd.Timedelta(days=7)))]

    closing_trend = calculate_trend(last_week_data['Close'])
    opening_trend = calculate_trend(last_week_data['Open'])

    trend_comparison = f"{closing_trend} vs {opening_trend}"

    closing_volume_corr = last_week_data['Close'].corr(last_week_data['Volume'])

    print(f"METRIC:Closing_Trend_7d\tVALUE:{closing_trend}\tUNIT:\tTYPE:str")
    print(f"METRIC:Opening_Trend_7d\tVALUE:{opening_trend}\tUNIT:\tTYPE:str")
    print(f"METRIC:Trend_Comparison\tVALUE:{trend_comparison}\tUNIT:\tTYPE:str")
    print(f"METRIC:Closing_Volume_Correlation\tVALUE:{closing_volume_corr}\tUNIT:\tTYPE:float")

if __name__ == "__main__":
    main()
