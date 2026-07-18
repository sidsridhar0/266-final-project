import pandas as pd
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Evaluate the strength of daily price movements through candlestick analysis.')
parser.add_argument('--data_path', type=str, required=True, help='Path to the data file (CSV format).')
parser.add_argument('--product_name', type=str, required=True, help='Name of the product to analyze.')
parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format.')

# Parse arguments
args = parser.parse_args()

# Load data
df = pd.read_csv(args.data_path, dtype={"Date": "str", "Product Name": "str", "Symbol": "str", 
                                        "Open": "float", "High": "float", "Low": "float", 
                                        "Close": "float", "Volume": "float"})

# Forward fill missing values
df.ffill(inplace=True)

# Filter data for given product and calculate metrics
df_product = df[(df['Product Name'] == args.product_name)]

# Define a function to calculate candlestick metrics
def calculate_candlestick_metrics(row):
    upper_wick = row['High'] - max(row['Open'], row['Close'])
    lower_wick = min(row['Open'], row['Close']) - row['Low']
    return upper_wick, lower_wick

# Apply calculation for each row in the DataFrame
df_product[['upper_wick', 'lower_wick']] = df_product.apply(calculate_candlestick_metrics, axis=1, result_type='expand')

# Filter by the given date
df_date = df_product[df_product['Date'] == args.date]

# Print results
for index, row in df_date.iterrows():
    print("METRIC:upper_wick_length\tVALUE:{:.4f}\tUNIT:\tTYPE:{}".format(row['upper_wick'], type(row['upper_wick']).__name__))
    print("METRIC:lower_wick_length\tVALUE:{:.4f}\tUNIT:\tTYPE:{}".format(row['lower_wick'], type(row['lower_wick']).__name__))
