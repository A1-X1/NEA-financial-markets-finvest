import pandas as pd
import numpy as np

def calculateSharpeRatio(data: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
    
    """
    Calculates the Annualised Sharpe Ratio.
    (Mean Annual Return - Risk Free Rate) / Annualised Volatility
    """

    if data is None or 'Daily_Return' not in data.columns:
        return 0.0

    # 1. Calculate Mean Daily Return and Daily Volatility
    mean_daily_return = data['Daily_Return'].mean()
    daily_volatility = data['Daily_Return'].std()

    if daily_volatility == 0 or np.isnan(daily_volatility):
        return 0.0

    # 2. Annualise the metrics (252 trading days in a year)
    annualised_return = mean_daily_return * 252
    annualised_volatility = daily_volatility * np.sqrt(252)

    # 3. Calculate Sharpe Ratio
    sharpe_ratio = (annualised_return - risk_free_rate) / annualised_volatility
    
    return round(sharpe_ratio, 2)