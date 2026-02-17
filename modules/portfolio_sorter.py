import yfinance as yf
import pandas as pd
import numpy as np

def calculate_sharpe_ratio(portfolio_items, risk_free_rate=0.02):
    # calculate an annualised sharpe ratio so it should always be 1 year so have the time period as default 1 year
    if not portfolio_items:
        return 0.0

    tickers = [item[0] for item in portfolio_items]
    quantities = {item[0]: item[1] for item in portfolio_items}

    try:
        # fetch 1 year of historical data
        data = yf.download(tickers, period="1y", progress=False)['Close']
        
        if data.empty:
            return 0.0

        # if only one ticker is provided, data is a Series
        if isinstance(data, pd.Series):
            portfolio_value = data * quantities[tickers[0]]
        else:
            # calculate daily portfolio value
            portfolio_value = pd.Series(0.0, index=data.index)
            for ticker in tickers:
                if ticker in data.columns:
                    portfolio_value += data[ticker] * quantities[ticker]

        # calculate daily returns
        daily_returns = portfolio_value.pct_change().dropna()
        
        if daily_returns.empty:
            return 0.0

        # annualised mean return and volatility
        # assuming 252 trading days for annualisation
        mean_return = daily_returns.mean() * 252
        volatility = daily_returns.std() * np.sqrt(252)

        if volatility == 0:
            return 0.0

        # return annualised sharpe ratio
        return (mean_return - risk_free_rate) / volatility

    except Exception as e:
        print(f"Error calculating Sharpe Ratio: {e}")
        return 0.0

def merge_sort_portfolios(portfolios, descending=True):
    # custom mergesort function that takes in different portfolios and sorts them
    # sorting is done off of the sharpe ratio of the portfolio
    
    # helper function for recursion
    def _merge_sort(arr):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = _merge_sort(arr[:mid])
        right = _merge_sort(arr[mid:])

        return _merge(left, right)

    def _merge(left, right):
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            # compare based on pre-calculated sharpe ratio
            # descending order means larger sharpe ratio first
            condition = left[i]['sharpe_ratio'] > right[j]['sharpe_ratio'] if descending else left[i]['sharpe_ratio'] < right[j]['sharpe_ratio']
            
            if condition:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    # pre-calculate sharpe ratios to avoid redundant calculations during sort
    processed_portfolios = []
    for p in portfolios:
        # p is expected to be a dict with 'name' and 'items'
        # item is (ticker, quantity)
        sr = calculate_sharpe_ratio(p['items'])
        p_with_sr = p.copy()
        p_with_sr['sharpe_ratio'] = sr
        processed_portfolios.append(p_with_sr)

    return _merge_sort(processed_portfolios)
