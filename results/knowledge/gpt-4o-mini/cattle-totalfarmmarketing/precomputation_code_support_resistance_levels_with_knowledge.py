import pandas as pd
import argparse

def calculate_support_resistance(data, date_of_interest):
    closing_prices = data['Close']
    
    # Find support levels (price level tested and not broken on downside)
    support_level = closing_prices[(closing_prices.shift(1) > closing_prices) & 
                                    (closing_prices.shift(-1) >= closing_prices)].value_counts().idxmax()

    # Find resistance levels (price level tested and not broken on upside)
    resistance_level = closing_prices[(closing_prices.shift(1) < closing_prices) & 
                                       (closing_prices.shift(-1) <= closing_prices)].value_counts().idxmax()

    return support_level, resistance_level

def main(data_path, product_name, date_of_interest):
    df = pd.read_csv(data_path)
    df = df[["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"]]

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

    df.ffill()

    df = df[(df['Product Name'] == product_name) & 
            (df['Date'] >= (pd.to_datetime(date_of_interest) - pd.Timedelta(days=30))) & 
            (df['Date'] <= pd.to_datetime(date_of_interest))]

    if len(df) < 2:
        raise ValueError("Insufficient data to calculate support/resistance levels.")

    support_level, resistance_level = calculate_support_resistance(df, date_of_interest)

    current_price = df.iloc[-1]['Close']

    print(f"METRIC:support_level\tVALUE:{support_level}\tUNIT:USD\tTYPE:float")
    print(f"METRIC:resistance_level\tVALUE:{resistance_level}\tUNIT:USD\tTYPE:float")
    print(f"METRIC:current_price\tVALUE:{current_price}\tUNIT:USD\tTYPE:float")
    print(f"METRIC:current_price_vs_support\tVALUE:{current_price - support_level}\tUNIT:USD\tTYPE:float")
    print(f"METRIC:current_price_vs_resistance\tVALUE:{current_price - resistance_level}\tUNIT:USD\tTYPE:float")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument("--product_name", type=str, required=True)
    parser.add_argument("--date", type=str, required=True)
    args = parser.parse_args()

    main(args.data_path, args.product_name, args.date)
