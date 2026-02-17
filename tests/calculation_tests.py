import sys
import os

# Adds the parent directory to the system path to prevent import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.calculations import calculateSharpeRatio, calculateVolatility, calculateTotalReturn, generate_gbm_paths

# testing gbm with params
s0 = 100
drift = 0.1
volatility = -0.5
numSims = 10
numSteps = 100
dt = 1/252

path1 = generate_gbm_paths(s0, drift, volatility, numSims, numSteps, dt)

print(path1)