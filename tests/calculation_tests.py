import sys
import os
import time


# Adds the parent directory to the system path to prevent import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.calculations import calculateSharpeRatio, calculateVolatility, calculateTotalReturn, generate_gbm_paths, generate_gbm_paths_pure_python

# testing gbm with params
s0 = 100
drift = 0.1
volatility = 0.2
numSims = 1000
numSteps = 100
dt = 1/252

start1 = time.perf_counter()
path1 = generate_gbm_paths(s0, drift, volatility, numSims, numSteps, dt)
end1 = time.perf_counter()

# print(path1)
print(f"\n Optimised code: {(end1 - start1)*1000:.3f} ms \n")

start2 = time.perf_counter()
path2 = generate_gbm_paths_pure_python(s0, drift, volatility, numSims, numSteps, dt)
end2 = time.perf_counter()

# print(path2)
print(f"\n Pure python code: {(end2 - start2)*1000:.3f} ms \n")


