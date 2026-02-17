import sys
import os
import unittest
import numpy as np

# Add the project root to sys.path to allow importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.simulationEngine import SimulationEngine

class TestSimulationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SimulationEngine()

    def test_validation_volatility(self):
        with self.assertRaises(ValueError):
            self.engine.volatility = -0.1
        self.engine.volatility = 0.5
        self.assertEqual(self.engine.volatility, 0.5)

    def test_validation_simulations(self):
        with self.assertRaises(ValueError):
            self.engine.num_simulations = 0
        with self.assertRaises(ValueError):
            self.engine.num_simulations = 10001
        self.engine.num_simulations = 500
        self.assertEqual(self.engine.num_simulations, 500)

    def test_run_simulation_shape(self):
        self.engine.num_simulations = 10
        self.engine.num_steps = 100
        paths = self.engine.run_simulation()
        # 10 paths, 101 steps (0 to 100)
        self.assertEqual(paths.shape, (10, 101))
        # initial price should be 100.0 (default)
        self.assertTrue(np.all(paths[:, 0] == 100.0))

if __name__ == '__main__':
    unittest.main()
