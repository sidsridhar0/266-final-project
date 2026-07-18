import pandas as pd
import argparse
import numpy as np

def calculate_metrics(data_path, product_name, date):
    # Read the data into DataFrame
    data = pd.read_csv(data_path, usecols=["Date", "Product Name", "Close"])
    
    # Convert data types
    data["Date"] = pd.to_datetime(data["Date"])
    data["Close"] = data["Close"].astype(float)
    
    # Filter the data for the specified product
    data = data[data["Product Name"] == product_name]
    
    # Forward fill missing values
    data.ffill(inplace=True)
    
    # Ensure data is sorted by date
    data.sort_values(by="Date", inplace=True)

    # Calculate current monthly return
    data["Prev Close"] = data["Close"].shift(1)
    data["Current Monthly Return"] = (data["Close"] / data["Prev Close"]) - 1
    
    # Extract the month and year from date
    data["YearMonth"] = data["Date"].dt.to_period("M")
    
    # Calculate historical monthly average returns
    average_monthly_return = data.groupby(data["Date"].dt.month)["Current Monthly Return"].mean()
    
    # Calculate overall average monthly return
    overall_average_monthly_return = average_monthly_return.mean()
    
    # Calculate the seasonal index
    seasonal_index = average_monthly_return / overall_average_monthly_return
    
    # Filter by the date of interest for the current monthly return
    current_date = pd.to_datetime(date)
    current_month_data = data[(data["Date"].dt.year == current_date.year) & 
                              (data["Date"].dt.month == current_date.month)]
    
    # Calculate metrics for the current month
    current_month_return = current_month_data.iloc[-1]["Current Monthly Return"]
    current_month_seasonal_index = seasonal_index[current_date.month]
    
    # Print results
    print("METRIC:Current Monthly Return\tVALUE:{:.4f}\tUNIT:percent\tTYPE:float".format(current_month_return * 100))
    print("METRIC:Seasonal Index\tVALUE:{:.4f}\tUNIT:ratio\tTYPE:float".format(current_month_seasonal_index))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True, help='Path to CSV data file')
    parser.add_argument('--product_name', type=str, required=True, help='Name of the product to analyze')
    parser.add_argument('--date', type=str, required=True, help='Date of interest in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    calculate_metrics(args.data_path, args.product_name, args.date)
