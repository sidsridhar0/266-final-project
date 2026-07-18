import pandas as pd
import argparse

def main(data_path, product_name, date):
    # Read the data into a pandas DataFrame
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])

    # Convert data types
    df["Date"] = pd.to_datetime(df["Date"])
    df["Product Name"] = df["Product Name"].astype(str)
    df["Symbol"] = df["Symbol"].astype(str)
    df["Open"] = df["Open"].astype(float)
    df["High"] = df["High"].astype(float)
    df["Low"] = df["Low"].astype(float)
    df["Close"] = df["Close"].astype(float)
    df["Volume"] = df["Volume"].astype(float)

    # Handle missing/invalid values
    df.ffill(inplace=True)

    # Filter the data for the last 30 days including the date of interest
    target_date = pd.to_datetime(date)
    start_date = target_date - pd.Timedelta(days=30)
    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= target_date) & (df['Product Name'] == product_name)]

    # Critical Support and Resistance Levels Calculation
    support_level = filtered_data['Low'].min()
    resistance_level = filtered_data['High'].max()
    
    current_price = filtered_data.loc[filtered_data['Date'] == target_date, 'Close'].values[0]

    # Print results
    print(f'METRIC:Support_Level\tVALUE:{support_level}\tUNIT:USD\tTYPE:float')
    print(f'METRIC:Resistance_Level\tVALUE:{resistance_level}\tUNIT:USD\tTYPE:float')
    print(f'METRIC:Current_Price_Position\tVALUE:{current_price}\tUNIT:USD\tTYPE:float')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product (e.g., cattle)')
    parser.add_argument('--date', type=str, required=True, help='The date of interest in YYYY-MM-DD format')

    args = parser.parse_args()
    main(args.data_path, args.product_name, args.date)
