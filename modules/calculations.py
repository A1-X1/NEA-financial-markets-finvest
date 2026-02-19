import pandas as pd
import numpy as np
from numba import njit, prange
from datetime import time, datetime

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
def generate_gbm_paths(s0, drift, vol, num_sims, num_steps, dt):
    # s0: initial price
    # drift: expected annual return
    # vol: annual volatility
    # num_sims: paths to generate
    # num_steps: time steps per path
    # dt: time increment

    # input validation
    if (vol < 0):
        raise ValueError("Volatility cannot be negative")
    if (s0 <= 0):
        raise ValueError("Initial price must be positive")
    if (drift < 0):
        raise ValueError("Drift must be positive")
    if (num_sims <= 0):
        raise ValueError("Number of simulations must be positive")
    if (num_sims > 10000):
        raise ValueError("Number of simulations must be less than or equal to 10000")
    if (num_steps <= 0):
        raise ValueError("Number of steps must be positive")
    if (dt <= 0):
        raise ValueError("Time increment must be positive")

    
    # paths matrix (simulations x steps)
    paths = np.zeros((num_sims, num_steps + 1))
    paths[:, 0] = s0
    
    # prange used for parallel execution
    for i in prange(num_sims):
        # generate all shocks for this path at once (vectorized)
        shocks = np.random.standard_normal(num_steps)
        
        # calculate log returns (vectorized)
        drift_term = (drift - 0.5 * vol**2) * dt
        diffusion_term = vol * np.sqrt(dt) * shocks
        log_returns = drift_term + diffusion_term
        
        # calculate prices using cumulative sum (vectorized)
        cumulative_returns = np.cumsum(log_returns)
        paths[i, 1:] = s0 * np.exp(cumulative_returns)
            
    return paths


import math
import random

def generate_gbm_paths_pure_python(
    initial_price,
    expected_return,
    volatility,
    number_of_simulations,
    steps_per_path,
    time_step
):
    # ---- input validation ----
    if volatility < 0:
        raise ValueError("Volatility cannot be negative")
    if initial_price <= 0:
        raise ValueError("Initial price must be positive")
    if expected_return < 0:
        raise ValueError("Expected return (drift) must be positive")
    if number_of_simulations <= 0:
        raise ValueError("Number of simulations must be positive")
    if number_of_simulations > 10000:
        raise ValueError("Number of simulations must be <= 10000")
    if steps_per_path <= 0:
        raise ValueError("Number of steps must be positive")
    if time_step <= 0:
        raise ValueError("Time step must be positive")

    # ---- precomputed constants ----
    drift_component = (expected_return - 0.5 * volatility * volatility) * time_step
    diffusion_scale = volatility * math.sqrt(time_step)

    # ---- allocate output ----
    price_paths = [
        [0.0] * (steps_per_path + 1)
        for _ in range(number_of_simulations)
    ]

    # ---- simulate paths ----
    for simulation_index in range(number_of_simulations):
        current_price = initial_price
        price_paths[simulation_index][0] = current_price

        for step_index in range(steps_per_path):
            standard_normal_shock = random.gauss(0.0, 1.0)
            growth_factor = math.exp(
                drift_component + diffusion_scale * standard_normal_shock
            )
            current_price *= growth_factor
            price_paths[simulation_index][step_index + 1] = current_price

    return price_paths
