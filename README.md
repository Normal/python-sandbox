# Python Data Analysis Project

This project is set up with common data analysis and visualization libraries:
- pandas: For data manipulation and analysis
- numpy: For numerical computing
- matplotlib: For data visualization
- yfinance: For fetching financial data from Yahoo Finance

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

- `src/`: Contains the main Python scripts
  - `ma_trading_strategy.py`: Example script demonstrating stock data analysis
- `data/`: Directory for storing data files
- `notebooks/`: Jupyter notebooks for analysis
- `requirements.txt`: Project dependencies

## Example Usage

Check out the example script in `src/ma_trading_strategy.py` for a demonstration of how to use these libraries together. 

To run the updated code:
```bash
python src/ma_trading_strategy.py
```

The script will:
1. Create timestamped files in each directory
2. Print the location of each saved file
3. Show the plot
4. Display statistics

Each file is timestamped to:
- Keep historical data
- Prevent overwriting
- Track when the analysis was run

Would you like me to:
1. Show you how to read and analyze these saved files?
2. Add more types of data or calculations?
3. Modify the file formats or naming conventions? 
