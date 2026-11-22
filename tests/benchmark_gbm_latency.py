import sys
import os
import time
import numpy as np

# adds the parent directory to the system path to prevent import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.calculations import generate_gbm_paths, generate_gbm_paths_pure_python

# usage: python tests/benchmark_gbm_latency.py
# measures p50 / p90 / p99 latency over many timed runs after warm-up


def benchmark(function, num_sims, num_steps, iterations, warmup):
    args = (100.0, 0.08, 0.2, num_sims, num_steps, 1 / 252)

    # warm-up runs trigger jit compilation and fill cpu caches, so they are not timed
    for _ in range(warmup):
        function(*args)

    timings_ms = np.empty(iterations)
    for k in range(iterations):
        start = time.perf_counter_ns()
        function(*args)
        timings_ms[k] = (time.perf_counter_ns() - start) / 1e6

    p50, p90, p99 = np.percentile(timings_ms, [50, 90, 99])
    return p50, p90, p99


if __name__ == '__main__':
    print(f"cpu cores: {os.cpu_count()}")
    for num_sims in (1000, 10000):
        cases = [
            ("numba parallel", generate_gbm_paths, 300, 20),
            ("pure python", generate_gbm_paths_pure_python, 5 if num_sims == 1000 else 2, 1),
        ]
        for name, function, iterations, warmup in cases:
            p50, p90, p99 = benchmark(function, num_sims, 252, iterations, warmup)
            print(f"{num_sims:>5} paths x 252 steps | {name:15s} | "
                  f"p50 {p50:8.2f} ms | p90 {p90:8.2f} ms | p99 {p99:8.2f} ms | runs {iterations}")
