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
    
    # Get currency information
    info = stock.info
    currency = info.get('currency', 'USD')
    
    return df, currency

def fetch_exchange_rate(base_currency, target_currency, period='1mo', interval='1h'):
    """
    Fetch exchange rate data between two currencies
    """
    if base_currency == target_currency:
        return None
    
    # Create a forex pair symbol
    forex_symbol = f"{base_currency}{target_currency}=X"
    
    try:
        forex = yf.Ticker(forex_symbol)
        df_forex = forex.history(period=period, interval=interval)
        return df_forex
    except:
        print(f"Warning: Could not fetch exchange rate for {forex_symbol}")
        return None

def calculate_signals(df, df_forex=None, base_currency='USD'):
    """
    Calculate trading signals based on multiple MA periods with exchange rate consideration
    """
    # Calculate different moving averages
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA30'] = df['Close'].rolling(window=30).mean()
    
    # Calculate daily returns in local currency
    df['Returns'] = df['Close'].pct_change()
    
    # Apply exchange rate if available
    if df_forex is not None:
        # Merge exchange rate data with price data
        df = df.join(df_forex['Close'], how='left')
        df.rename(columns={'Close': 'Exchange_Rate'}, inplace=True)
        
        # Forward fill missing exchange rate values
        df['Exchange_Rate'] = df['Exchange_Rate'].ffill()
        
        # Calculate returns in base currency
        df['Returns_Base'] = df['Returns'] * df['Exchange_Rate'].pct_change()
    else:
        # If no exchange rate data, use local currency returns
        df['Returns_Base'] = df['Returns']
    
    # Generate signals for each MA
    for ma in ['MA10', 'MA20', 'MA30']:
        df[f'{ma}_Signal'] = 0
        # Buy signal when price crosses above MA
        df.loc[df['Close'] > df[ma], f'{ma}_Signal'] = 1
        # Sell signal when price crosses below MA
        df.loc[df['Close'] < df[ma], f'{ma}_Signal'] = -1
        
        # Calculate strategy returns in base currency
        df[f'{ma}_Returns'] = df[f'{ma}_Signal'].shift(1) * df['Returns_Base']
        df[f'{ma}_Cumulative_Returns'] = (1 + df[f'{ma}_Returns']).cumprod()
    
    # Calculate pure Buy & Hold returns in base currency (never sells)
    df['BH_Returns'] = df['Returns_Base']  # Always invested
    df['BH_Cumulative_Returns'] = (1 + df['BH_Returns']).cumprod()
    
    return df

def calculate_performance_metrics(df, strategy):
    """
    Calculate performance metrics for the strategy
    """
    # Total return
    total_return = df[f'{strategy}_Cumulative_Returns'].iloc[-1] - 1
    
    # Annualized return
    days = (df.index[-1] - df.index[0]).days
    annualized_return = (1 + total_return) ** (365/days) - 1
    
    # Maximum drawdown
    cumulative_returns = df[f'{strategy}_Cumulative_Returns']
    rolling_max = cumulative_returns.expanding().max()
    drawdowns = cumulative_returns / rolling_max - 1
    max_drawdown = drawdowns.min()
    
    # Sharpe Ratio (assuming risk-free rate of 0.02)
    risk_free_rate = 0.02
    excess_returns = df[f'{strategy}_Returns'] - risk_free_rate/252  # Daily risk-free rate
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    # Win rate
    winning_days = (df[f'{strategy}_Returns'] > 0).sum()
    total_days = df[f'{strategy}_Returns'].count()
    win_rate = winning_days / total_days
    
    return {
        'Total Return': f'{total_return:.2%}',
        'Annualized Return': f'{annualized_return:.2%}',
        'Maximum Drawdown': f'{max_drawdown:.2%}',
        'Sharpe Ratio': f'{sharpe_ratio:.2f}',
        'Win Rate': f'{win_rate:.2%}'
    }

def plot_strategy(df, symbol, currency, base_currency='USD'):
    """
    Plot the trading strategy results for all MA periods
    """
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot 1: Price and MAs
    ax1.plot(df.index, df['Close'], label=f'Close Price ({currency})', color='black', alpha=0.7)
    ax1.plot(df.index, df['MA20'], label='20-hour MA', color='red', linestyle='--')
    
    # Plot MA20 signals
    ma20_buy = df[df['MA20_Signal'] == 1].index
    ma20_sell = df[df['MA20_Signal'] == -1].index
    
    ax1.scatter(ma20_buy, df.loc[ma20_buy, 'Close'], 
                marker='^', color='green', label='MA20 Buy', s=100)
    ax1.scatter(ma20_sell, df.loc[ma20_sell, 'Close'], 
                marker='v', color='red', label='MA20 Sell', s=100)
    
    # Add exchange rate if available
    if 'Exchange_Rate' in df.columns:
        ax1_twin = ax1.twinx()
        ax1_twin.plot(df.index, df['Exchange_Rate'], label=f'{currency}/{base_currency}', 
                     color='purple', linestyle=':', alpha=0.7)
        ax1_twin.set_ylabel(f'Exchange Rate ({currency}/{base_currency})')
        ax1_twin.legend(loc='upper right')
    
    ax1.set_title(f'{symbol} Price and MA20 vs Buy & Hold Comparison')
    ax1.set_ylabel(f'Price ({currency})')
    ax1.legend(loc='upper left')
    ax1.grid(True)
    
    # Format x-axis to show dates nicely
    ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Cumulative Returns
    ax2.plot(df.index, df['BH_Cumulative_Returns'], 
             label='Buy & Hold (Never Sells)', color='blue', linestyle='-')
    ax2.plot(df.index, df['MA20_Cumulative_Returns'], 
             label='MA20 Strategy', color='red')
    
    # Add annotations for key points
    bh_return = df['BH_Cumulative_Returns'].iloc[-1] - 1
    ma20_return = df['MA20_Cumulative_Returns'].iloc[-1] - 1
    
    ax2.annotate(f'BH Return: {bh_return:.2%}', 
                 xy=(df.index[-1], df['BH_Cumulative_Returns'].iloc[-1]),
                 xytext=(10, 10), textcoords='offset points')
    ax2.annotate(f'MA20 Return: {ma20_return:.2%}', 
                 xy=(df.index[-1], df['MA20_Cumulative_Returns'].iloc[-1]),
                 xytext=(10, -10), textcoords='offset points')
    
    ax2.set_title(f'Cumulative Returns: Buy & Hold vs MA20 (in {base_currency})')
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
    symbol = 'AAPL'  # Can be changed to any stock symbol
    period = '1mo'  # Last month
    interval = '1h'  # Hourly data
    base_currency = 'USD'  # Base currency for returns
    
    # Fetch data
    print(f"Fetching {symbol} hourly data for the last month...")
    df, currency = fetch_stock_data(symbol, period, interval)
    
    # Fetch exchange rate if needed
    df_forex = None
    if currency != base_currency:
        print(f"Fetching exchange rate from {currency} to {base_currency}...")
        df_forex = fetch_exchange_rate(currency, base_currency, period, interval)
    
    # Calculate signals and returns
    print("Calculating trading signals...")
    df = calculate_signals(df, df_forex, base_currency)
    
    # Calculate and print performance metrics
    print("\nStrategy Performance Metrics:")
    print(f"\nBuy & Hold Strategy (Never Sells) - Returns in {base_currency}:")
    metrics = calculate_performance_metrics(df, 'BH')
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    
    print(f"\nMA20 Strategy - Returns in {base_currency}:")
    metrics = calculate_performance_metrics(df, 'MA20')
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    
    # Plot results
    print("\nGenerating plots...")
    plot_strategy(df, symbol, currency, base_currency)

if __name__ == "__main__":
    main() 