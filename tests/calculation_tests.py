from modules.calculations import calculateSharpeRatio, calculateVolatility, calculateTotalReturn, generate_gbm_paths
import pandas as pd

# testing gbm

path1 = generate_gbm_paths(100, 0.1, 0.2, 10, 100, 1/252)


print(path1)