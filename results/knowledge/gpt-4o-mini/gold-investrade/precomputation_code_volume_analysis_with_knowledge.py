import pandas as pd
import argparse

def main(data_path, product_name, date):
    # Read data into DataFrame
    df = pd.read_csv(data_path, usecols=["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    
    # Convert data types
    df['Date'] = pd.to_datetime(df['Date'])
    df['Product Name'] = df['Product Name'].astype(str)
    df['Symbol'] = df['Symbol'].astype(str)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(float)
    
    # Handle missing values
    df.ffill(inplace=True)

    # Filter data by product name
    df_product = df[df['Product Name'] == product_name]

    # Get current date of interest
    date_of_interest = pd.to_datetime(date)
    
    # Calculate current volume
    current_volume = df_product.loc[df_product['Date'] == date_of_interest, 'Volume'].sum()
    
    # Calculate 30-day average volume
    df_30_days = df_product[(df_product['Date'] < date_of_interest) & (df_product['Date'] >= date_of_interest - pd.Timedelta(days=30))]
    avg_30_day_volume = df_30_days['Volume'].mean()
    
    # Print results
    print(f'METRIC:current_volume\tVALUE:{current_volume}\tUNIT:volume\tTYPE:float')
    print(f'METRIC:avg_30_day_volume\tVALUE:{avg_30_day_volume}\tUNIT:volume\tTYPE:float')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument("--product_name", type=str, required=True)
    parser.add_argument("--date", type=str, required=True)
    
    args = parser.parse_args()
    main(args.data_path, args.product_name, args.date)
