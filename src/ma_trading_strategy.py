import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def fetch_stock_data(symbol, period='1mo', interval='1h'):
    """
    Fetch stock data using yfinance with specified interval
    """
    stock = yf.Ticker(symbol)
    df = stock.history(period=period, interval=interval)
    return df

def calculate_signals(df):
    """
    Calculate trading signals based on MA20
    """
    # Calculate 20-day moving average
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # Generate signals
    df['Signal'] = 0
    # Buy signal when price crosses above MA20
    df.loc[df['Close'] > df['MA20'], 'Signal'] = 1
    # Sell signal when price crosses below MA20
    df.loc[df['Close'] < df['MA20'], 'Signal'] = -1
    
    # Calculate daily returns
    df['Returns'] = df['Close'].pct_change()
    
    # Calculate strategy returns
    df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
    
    # Calculate cumulative returns
    df['Cumulative_Returns'] = (1 + df['Returns']).cumprod()
    df['Strategy_Cumulative_Returns'] = (1 + df['Strategy_Returns']).cumprod()
    
    return df

def calculate_performance_metrics(df):
    """
    Calculate performance metrics for the strategy
    """
    # Total return
    total_return = df['Strategy_Cumulative_Returns'].iloc[-1] - 1
    
    # Annualized return
    days = (df.index[-1] - df.index[0]).days
    annualized_return = (1 + total_return) ** (365/days) - 1
    
    # Maximum drawdown
    cumulative_returns = df['Strategy_Cumulative_Returns']
    rolling_max = cumulative_returns.expanding().max()
    drawdowns = cumulative_returns / rolling_max - 1
    max_drawdown = drawdowns.min()
    
    # Sharpe Ratio (assuming risk-free rate of 0.02)
    risk_free_rate = 0.02
    excess_returns = df['Strategy_Returns'] - risk_free_rate/252  # Daily risk-free rate
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    # Win rate
    winning_days = (df['Strategy_Returns'] > 0).sum()
    total_days = df['Strategy_Returns'].count()
    win_rate = winning_days / total_days
    
    return {
        'Total Return': f'{total_return:.2%}',
        'Annualized Return': f'{annualized_return:.2%}',
        'Maximum Drawdown': f'{max_drawdown:.2%}',
        'Sharpe Ratio': f'{sharpe_ratio:.2f}',
        'Win Rate': f'{win_rate:.2%}'
    }

def plot_strategy(df, symbol):
    """
    Plot the trading strategy results
    """
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot 1: Price and MA20
    ax1.plot(df.index, df['Close'], label='Close Price', color='blue')
    ax1.plot(df.index, df['MA20'], label='20-hour MA', color='red', linestyle='--')
    
    # Plot buy/sell signals
    buy_signals = df[df['Signal'] == 1].index
    sell_signals = df[df['Signal'] == -1].index
    
    ax1.scatter(buy_signals, df.loc[buy_signals, 'Close'], 
                marker='^', color='green', label='Buy Signal', s=100)
    ax1.scatter(sell_signals, df.loc[sell_signals, 'Close'], 
                marker='v', color='red', label='Sell Signal', s=100)
    
    ax1.set_title(f'{symbol} Price and MA20 Trading Signals (Last Month - Hourly)')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True)
    
    # Format x-axis to show dates nicely
    ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Cumulative Returns
    ax2.plot(df.index, df['Cumulative_Returns'], 
             label='Buy & Hold', color='blue')
    ax2.plot(df.index, df['Strategy_Cumulative_Returns'], 
             label='MA20 Strategy', color='green')
    ax2.set_title('Cumulative Returns')
    ax2.set_ylabel('Cumulative Returns')
    ax2.legend()
    ax2.grid(True)
    
    # Format x-axis for the second plot
    ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.show()

def main():
    # Parameters
    symbol = 'AAPL'
    period = '1mo'  # Last month
    interval = '1h'  # Hourly data
    
    # Fetch data
    print(f"Fetching {symbol} hourly data for the last month...")
    df = fetch_stock_data(symbol, period, interval)
    
    # Calculate signals and returns
    print("Calculating trading signals...")
    df = calculate_signals(df)
    
    # Calculate performance metrics
    print("Calculating performance metrics...")
    metrics = calculate_performance_metrics(df)
    
    # Print performance metrics
    print("\nStrategy Performance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    
    # Plot results
    print("\nGenerating plots...")
    plot_strategy(df, symbol)

if __name__ == "__main__":
    main() 