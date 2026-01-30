import pandas as pd
import numpy as np

# calculates the Sharpe Ratio
def calculateSharpeRatio(data: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
    if data is None or 'Daily_Return' not in data.columns:
        return 0.0

    # calculate mean daily return and daily volatility
    mean_daily_return = data['Daily_Return'].mean()
    daily_volatility = data['Daily_Return'].std()

    if daily_volatility == 0 or np.isnan(daily_volatility):
        return 0.0

    # annualise the metrics (252 trading days in a year)
    annualised_return = mean_daily_return * 252
    annualised_volatility = daily_volatility * np.sqrt(252)

    # calculate sharpe ratio
    sharpe_ratio = (annualised_return - risk_free_rate) / annualised_volatility
    
    return round(sharpe_ratio, 2)

# calculate annualised volatility (standard deviation of returns)
def calculateVolatility(data_frame):
    daily_returns = data_frame['Close'].pct_change().dropna()
    
    # 252 is the standard number of trading days in a year
    annualised_vol = daily_returns.std() * np.sqrt(252)
    return annualised_vol

# calculate the percentage growth over the specific period
def calculateTotalReturn(data_frame):
    initial_price = data_frame['Close'].iloc[0]
    final_price = data_frame['Close'].iloc[-1]
    percentage_growth = ((final_price - initial_price) / initial_price) * 100
    return percentage_growth