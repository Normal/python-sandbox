import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def fetch_stock_data(symbol, period='1y'):
    """
    Fetch stock data using yfinance
    """
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    return df

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
    # Save the figure
    plt.savefig('data/stock_analysis.png')
    # Show the plot and keep it open
    plt.show()
    # Note: plt.close() is removed to keep the window open

def main():
    # Example: Analyze Apple stock
    symbol = 'AAPL'
    
    # Show detailed ticker information
    print("Fetching ticker information...")
    ticker = show_ticker_info(symbol)
    
    # Fetch data
    print(f"\nFetching historical data for {symbol}...")
    df = fetch_stock_data(symbol)
    
    # Calculate indicators
    print("Calculating technical indicators...")
    df = calculate_technical_indicators(df)
    
    # Create visualization
    print("Creating visualization...")
    plot_stock_analysis(df, symbol)
    
    # Print some basic statistics
    print("\nBasic Statistics:")
    print(f"Average Daily Return: {df['Returns'].mean():.2%}")
    print(f"Volatility: {df['Volatility'].mean():.2%}")
    print(f"Current Price: ${df['Close'][-1]:.2f}")
    
    print("\nAnalysis complete! Check data/stock_analysis.png for the visualization.")

if __name__ == "__main__":
    main() 