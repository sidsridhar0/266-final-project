import pandas as pd
import numpy as np
from argparse import ArgumentParser
from pandas import DataFrame

def calculate_rsi(df: DataFrame, period: int = 14) -> pd.Series:
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI

def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def calculate_macd(df: DataFrame) -> (pd.Series, pd.Series):
    ema_12 = calculate_ema(df['Close'], 12)
    ema_26 = calculate_ema(df['Close'], 26)
    macd_line = ema_12 - ema_26
    macd_signal = calculate_ema(macd_line, 9)
    return macd_line, macd_signal

def print_results(metric, value, unit, data_type):
    print(f"METRIC:{metric}\tVALUE:{value}\tUNIT:{unit}\tTYPE:{data_type}")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--product_name', type=str, required=True)
    parser.add_argument('--date', type=str, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.data_path, usecols=["Date", "Product Name", "Open", "High", "Low", "Close", "Volume"])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Product Name'] == args.product_name]
    df = df.sort_values(by='Date').reset_index(drop=True)
    df = df.ffill()

    # Calculate required metrics
    df['RSI'] = calculate_rsi(df)
    df['MACD_line'], df['MACD_signal'] = calculate_macd(df)
    
    # Filter by the date of interest
    date_of_interest = pd.to_datetime(args.date)
    df_filtered = df[df['Date'] <= date_of_interest].iloc[-1]

    # Print RSI
    rsi_value = df_filtered['RSI']
    print_results("RSI_14", f"{rsi_value:.2f}", "", "float")

    # Print MACD Line
    macd_line_value = df_filtered['MACD_line']
    print_results("MACD_line", f"{macd_line_value:.2f}", "", "float")

    # Print MACD Signal
    macd_signal_value = df_filtered['MACD_signal']
    print_results("MACD_signal", f"{macd_signal_value:.2f}", "", "float")
