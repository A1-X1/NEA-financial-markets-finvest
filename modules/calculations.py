import pandas as pd
import numpy as np
from numba import njit, prange

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

# generates monte carlo paths using gbm
# njit decorator used to compile to machine code for speed
# parallel=True allows for multithreaded execution across sims
@njit(parallel=True)
def generate_gbm_paths(s0, drift, vol, num_sims, num_steps, dt):
    # s0: initial price
    # drift: expected annual return
    # vol: annual volatility
    # num_sims: paths to generate
    # num_steps: time steps per path
    # dt: time increment
    
    # paths matrix (simulations x steps)
    paths = np.zeros((num_sims, num_steps + 1))
    paths[:, 0] = s0
    
    # prange used for parallel execution
    for i in prange(num_sims):
        # generate all shocks for this path at once (vectorized)
        shocks = np.random.standard_normal(num_steps)
        
        # calculate log returns (vectorized)
        # log_ret = (mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*shock
        drift_term = (drift - 0.5 * vol**2) * dt
        diffusion_term = vol * np.sqrt(dt) * shocks
        log_returns = drift_term + diffusion_term
        
        # calculate prices using cumulative sum (vectorized)
        # S_t = S_0 * exp(cumsum(log_returns))
        cumulative_returns = np.cumsum(log_returns)
        paths[i, 1:] = s0 * np.exp(cumulative_returns)
            
    return paths