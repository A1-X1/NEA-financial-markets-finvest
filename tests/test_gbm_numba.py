import sys
import os
import unittest
import numpy as np

# adds the parent directory to the system path to prevent import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.calculations import generate_gbm_paths


class TestNumbaGBM(unittest.TestCase):
    def test_shape_and_initial_price(self):
        paths = generate_gbm_paths(100.0, 0.05, 0.2, 50, 252, 1 / 252)
        self.assertEqual(paths.shape, (50, 253))
        self.assertTrue(np.all(paths[:, 0] == 100.0))

    def test_prices_stay_positive_and_finite(self):
        paths = generate_gbm_paths(100.0, 0.05, 0.6, 2000, 252, 1 / 252)
        self.assertTrue(np.all(paths > 0))
        self.assertTrue(np.all(np.isfinite(paths)))

    def test_accepts_integer_inputs(self):
        paths = generate_gbm_paths(100, 0, 0, 10, 5, 1)
        self.assertTrue(np.allclose(paths, 100.0))

    def test_zero_volatility_is_deterministic(self):
        # with no volatility every path should grow at exactly the drift rate
        paths = generate_gbm_paths(100.0, 0.1, 0.0, 5, 252, 1 / 252)
        expected = 100.0 * np.exp(0.1 * np.arange(253) / 252)
        for row in paths:
            self.assertTrue(np.allclose(row, expected))

    def test_terminal_mean_matches_theory(self):
        # for gbm the expected terminal price is s0 * exp(drift * t)
        s0, drift, vol = 100.0, 0.08, 0.2
        paths = generate_gbm_paths(s0, drift, vol, 10000, 252, 1 / 252)
        terminal = paths[:, -1]
        expected = s0 * np.exp(drift)
        standard_error = terminal.std() / np.sqrt(len(terminal))
        self.assertLess(abs(terminal.mean() - expected), 5 * standard_error)

    def test_log_return_volatility_matches_input(self):
        paths = generate_gbm_paths(100.0, 0.05, 0.3, 5000, 252, 1 / 252)
        log_returns = np.diff(np.log(paths), axis=1)
        annualised_vol = log_returns.std() * np.sqrt(252)
        self.assertAlmostEqual(annualised_vol, 0.3, delta=0.005)

    def test_paths_are_independent(self):
        # paths running on different threads must not share random numbers
        paths = generate_gbm_paths(100.0, 0.05, 0.2, 1000, 50, 1 / 252)
        unique_rows = np.unique(paths[:, 1])
        self.assertEqual(len(unique_rows), 1000)

    def test_validation_still_applies(self):
        with self.assertRaises(ValueError):
            generate_gbm_paths(100.0, 0.05, -0.1, 10, 10, 1 / 252)
        with self.assertRaises(ValueError):
            generate_gbm_paths(0, 0.05, 0.2, 10, 10, 1 / 252)
        with self.assertRaises(ValueError):
            generate_gbm_paths(100.0, 0.05, 0.2, 10001, 10, 1 / 252)


if __name__ == '__main__':
    unittest.main()
