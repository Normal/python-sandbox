import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os

def fetch_stock_data(symbol, period='1y'):
    """
    Fetch stock data using yfinance
    """
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    return df, stock

def save_data(df, symbol, stock):
    """
    Save data in different formats and locations
    """
    # Create timestamp for unique filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save raw data (CSV)
    raw_file = f'data/raw/{symbol}_{timestamp}_raw.csv'
    df.to_csv(raw_file)
    print(f"Raw data saved to: {raw_file}")
    
    # Save processed data (CSV with calculated indicators)
    processed_df = calculate_technical_indicators(df.copy())
    processed_file = f'data/processed/{symbol}_{timestamp}_processed.csv'
    processed_df.to_csv(processed_file)
    print(f"Processed data saved to: {processed_file}")
    
    # Save company info (JSON)
    info_file = f'data/external/{symbol}_{timestamp}_info.json'
    with open(info_file, 'w') as f:
        json.dump(stock.info, f, indent=4)
    print(f"Company info saved to: {info_file}")
    
    # Save interim calculations (JSON)
    interim_data = {
        'daily_returns': df['Close'].pct_change().to_dict(),
        'volatility': df['Close'].pct_change().rolling(window=20).std().to_dict()
    }
    # Convert Timestamp index to string format for JSON serialization
    interim_data = {
        'daily_returns': {str(k): v for k, v in interim_data['daily_returns'].items()},
        'volatility': {str(k): v for k, v in interim_data['volatility'].items()}
    }
    interim_file = f'data/interim/{symbol}_{timestamp}_calculations.json'
    with open(interim_file, 'w') as f:
        json.dump(interim_data, f, indent=4)
    print(f"Interim calculations saved to: {interim_file}")
    
    return processed_df

def show_ticker_info(symbol):
    """
    Demonstrate what information is available from a Ticker object
    """
    ticker = yf.Ticker(symbol)
    
    print(f"\n=== {symbol} Ticker Information ===")
    
    # Basic Info
    info = ticker.info
    print("\nBasic Information:")
    print(f"Company Name: {info.get('longName', 'N/A')}")
    print(f"Sector: {info.get('sector', 'N/A')}")
    print(f"Industry: {info.get('industry', 'N/A')}")
    print(f"Market Cap: ${info.get('marketCap', 0):,.2f}")
    
    # Financial Data
    print("\nFinancial Data:")
    print(f"Current Price: ${info.get('currentPrice', 0):.2f}")
    print(f"52 Week High: ${info.get('fiftyTwoWeekHigh', 0):.2f}")
    print(f"52 Week Low: ${info.get('fiftyTwoWeekLow', 0):.2f}")
    
    # Company Description
    print("\nCompany Description:")
    print(info.get('longBusinessSummary', 'N/A')[:500] + "...")
    
    return ticker

def calculate_technical_indicators(df):
    """
    Calculate some basic technical indicators
    """
    # Calculate 20-day moving average
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # Calculate daily returns
    df['Returns'] = df['Close'].pct_change()
    
    # Calculate volatility (20-day rolling standard deviation of returns)
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    
    return df

def plot_stock_analysis(df, symbol):
    """
    Create a visualization of the stock data and indicators
    """
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot stock price and moving average
    ax1.plot(df.index, df['Close'], label='Close Price', color='blue')
    ax1.plot(df.index, df['MA20'], label='20-day MA', color='red', linestyle='--')
    ax1.set_title(f'{symbol} Stock Price and Technical Indicators')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True)
    
    # Plot volatility
    ax2.plot(df.index, df['Volatility'], label='Volatility', color='green')
    ax2.set_ylabel('Volatility')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    
    # Save the figure with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_file = f'data/processed/{symbol}_{timestamp}_analysis.png'
    plt.savefig(plot_file)
    print(f"Plot saved to: {plot_file}")
    
    # Show the plot and keep it open
    plt.show()

def main():
    # Example: Analyze Apple stock
    symbol = 'AAPL'
    
    # Show detailed ticker information
    print("Fetching ticker information...")
    ticker = show_ticker_info(symbol)
    
    # Fetch data
    print(f"\nFetching historical data for {symbol}...")
    df, stock = fetch_stock_data(symbol)
    
    # Save data in different formats
    print("\nSaving data in different formats...")
    processed_df = save_data(df, symbol, stock)
    
    # Create visualization
    print("\nCreating visualization...")
    plot_stock_analysis(processed_df, symbol)
    
    # Print some basic statistics
    print("\nBasic Statistics:")
    print(f"Average Daily Return: {processed_df['Returns'].mean():.2%}")
    print(f"Volatility: {processed_df['Volatility'].mean():.2%}")
    print(f"Current Price: ${processed_df['Close'][-1]:.2f}")

if __name__ == "__main__":
    main() 