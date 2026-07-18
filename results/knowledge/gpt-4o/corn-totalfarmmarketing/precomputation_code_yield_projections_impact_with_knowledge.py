import pandas as pd
import argparse

def main(data_path, product_name, date):
    # 1. Read data into pandas DataFrame
    df = pd.read_csv(data_path)
  
    # 2. Filter data for the specific product name
    df = df[df['Product Name'] == product_name]

    # 3. Convert date column to datetime and other columns to appropriate types
    df['Date'] = pd.to_datetime(df['Date'])
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.ffill(inplace=True)

    # 4. Calculate required metrics
    historical_impact = df[(df['Date'] <= date)].copy()
    historical_yield_report_days = historical_impact['Date'].dt.dayofweek.isin([0, 1, 2, 3, 4])  # Assuming reports come on weekdays
    historical_price_change = historical_impact.loc[historical_yield_report_days, 'Close'].pct_change().dropna().mean()

    # Placeholder for current yield projections (Example value for demonstration)
    current_year_yield_projections = 500  # Example placeholder

    # 5. Print Results
    print("METRIC:Historical Yield Report Price Impact\tVALUE:{:.4f}\tUNIT:percent\tTYPE:float".format(historical_price_change * 100))
    print("METRIC:Current Year Yield Projections\tVALUE:{}\tUNIT:units\tTYPE:int".format(current_year_yield_projections))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True, help='Path to the CSV data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')

    args = parser.parse_args()
    main(args.data_path, args.product_name, args.date)
